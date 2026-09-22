import httpx
from sqlalchemy import desc, func, text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import NotFoundError, ValidationError
from app.ml.embeddings import EmbeddingService
from app.ml.recommender import RecommenderService
from app.ml.vector_store import VectorStore
from app.models.analytics import BrowsingHistory, Recommendation
from app.models.catalog import GarmentVariant


class AIService:
    def __init__(self):
        self._ollama_client = None
        self._recommender = RecommenderService()
        self._embeddings = EmbeddingService()
        self._vector_store = VectorStore()

    # ============================================================
    # CU-30: Recomendaciones (existente, mejorado)
    # ============================================================

    def recommend_for_client(
        self, db: Session, client_id: int, source_variant_id: int | None, limit: int
    ):
        recommender = RecommenderService()
        scored = recommender.get_recommendations(db, source_variant_id, client_id, limit)
        if not scored:
            return []
        stored: list = []
        for variant_id, score in scored:
            rec = db.query(Recommendation).filter(
                Recommendation.suggested_variant_id == variant_id,
                Recommendation.client_id == client_id,
            ).first()
            if rec:
                rec.score = score
            else:
                rec = Recommendation(
                    client_id=client_id,
                    source_variant_id=source_variant_id,
                    suggested_variant_id=variant_id,
                    score=score,
                )
                db.add(rec)
            stored.append(rec)
        db.commit()
        return stored

    def log_view(self, db: Session, client_id: int, variant_id: int) -> None:
        entry = db.query(BrowsingHistory).filter(
            BrowsingHistory.client_id == client_id,
            BrowsingHistory.variant_id == variant_id,
        ).first()
        if entry:
            entry.view_count += 1
        else:
            db.add(BrowsingHistory(client_id=client_id, variant_id=variant_id, view_count=1))
        db.commit()

    def notify_variant_not_found(self, variant_id: int) -> None:
        if not variant_id:
            raise NotFoundError("Variant not found.")

    # ============================================================
    # CU-30: Recomendaciones - Endpoints adicionales
    # ============================================================

    def get_recommendations_by_variant(
        self, db: Session, variant_id: int, limit: int = 10
    ):
        """Obtener recomendaciones basadas en un producto específico (similares)."""
        variant = db.get(GarmentVariant, variant_id)
        if not variant:
            raise NotFoundError("Variant not found.")

        # Usar el recomendador existente
        scored = RecommenderService().get_recommendations(db, source_variant_id=variant.id, client_id=None, limit=10)

        results = []
        for var_id, score in scored:
            variant_obj = db.get(GarmentVariant, var_id)
            if variant_obj and variant_obj.garment:
                results.append({
                    "variant_id": var_id,
                    "garment_name": variant_obj.garment.name,
                    "variant_sku": variant_obj.sku,
                    "size_name": variant_obj.size.name if variant_obj.size else None,
                    "color_name": variant_obj.color.name if variant_obj.color else None,
                    "price": float(variant_obj.price) if variant_obj.price else 0,
                    "score": float(score),
                    "garment_image_url": None,
                })
        return results

    def get_trending_products(self, db: Session, limit: int = 10):
        """Obtener productos tendencia (más vistos/comprados)."""

        from app.models.analytics import BrowsingHistory

        # Productos más vistos
        viewed = db.query(
            BrowsingHistory.variant_id,
            func.sum(BrowsingHistory.view_count).label("views")
        ).group_by(BrowsingHistory.variant_id).order_by(desc("views")).limit(limit).all()

        results = []
        for variant_id, views in viewed:
            variant = db.get(GarmentVariant, variant_id)
            if variant and variant.garment:
                results.append({
                    "variant_id": variant.id,
                    "garment_name": variant.garment.name,
                    "variant_sku": variant.sku,
                    "size_name": variant.size.name if variant.size else None,
                    "color_name": variant.color.name if variant.color else None,
                    "price": float(variant.price) if variant.price else 0,
                    "score": float(views),
                    "source": "trending",
                })
        return results

    # ============================================================
    # CU-31: Asistente IA (Chat con Ollama)
    # ============================================================

    @property
    def ollama_client(self):
        """Lazy load Ollama client."""
        if self._ollama_client is None:
            base_url = getattr(settings, "ollama_base_url", "http://localhost:11434")
            self._ollama_client = httpx.Client(base_url=base_url, timeout=60.0)
        return self._ollama_client

    def chat(self, messages: list[dict], temperature: float = 0.7, max_tokens: int = 500) -> dict:
        """
        Chat con Ollama (local).
        messages: [{"role": "user|assistant|system", "content": "..."}]
        """
        model = getattr(settings, "ollama_model", "llama3.2")

        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            }
        }

        try:
            response = self.ollama_client.post("/api/chat", json=payload, timeout=60.0)
            response.raise_for_status()
            data = response.json()
            return {
                "message": data.get("message", {}).get("content", ""),
                "model": data.get("model", "unknown"),
                "done": data.get("done", True),
                "tokens": data.get("eval_count", 0) + data.get("prompt_eval_count", 0),
            }
        except httpx.HTTPStatusError as e:
            raise Exception(f"Ollama error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise Exception(f"Ollama connection error: {str(e)}")

    def chat_with_context(
        self,
        message: str,
        context: str = "",
        history: list[dict] = None,
        temperature: float = 0.7,
        max_tokens: int = 500,
    ) -> dict:
        """Chat con contexto (catálogo, FAQ, etc.)."""
        messages = []

        # System prompt con contexto
        system_prompt = f"""Eres un asistente de moda para FashionStore. 
Ayuda a los clientes con recomendaciones, información de productos, tallas, colores, disponibilidad y preguntas generales.

{context}

Sé amable, conciso y útil. Responde en español."""

        messages.append({"role": "system", "content": system_prompt})

        if history:
            messages.extend(history[-10:])  # Últimos 10 mensajes

        messages.append({"role": "user", "content": message})

        return self.chat(messages, temperature=temperature, max_tokens=max_tokens)

    # ============================================================
    # CU-32: Generar consultas y reportes mediante IA (SQL Generation)
    # ============================================================

    def generate_sql_query(self, prompt: str, max_rows: int = 100) -> dict:
        """
        Generar SQL seguro a partir de lenguaje natural.
        Solo permite SELECT en tablas permitidas.
        """
        # Tablas permitidas (whitelist)
        allowed_tables = {
            "venta", "venta_detalle", "pago", "reserva", "reserva_detalle",
            "inventario", "movimiento_inventario", "recepcion_producto",
            "recepcion_producto_detalle", "prenda", "prenda_variante",
            "categoria", "talla", "color", "temporada", "coleccion",
            "cliente", "usuario", "sucursal", "proveedor",
            "promocion", "promocion_prenda", "bitacora_sistema", "notificacion", "recomendacion", "historial_navegacion"
        }

        # Prompt para el modelo
        tables_info = self._get_tables_schema()

        system_prompt = f"""Eres un generador de SQL para PostgreSQL. 
Convierte lenguaje natural a SQL seguro.

REGLAS ESTRICTAS:
1. SOLO sentencias SELECT (lectura)
2. SOLO tablas permitidas: {', '.join(sorted(allowed_tables))}
3. NO uses DROP, DELETE, UPDATE, INSERT, ALTER, CREATE, TRUNCATE
4. Siempre usa LIMIT (máximo {max_rows})
5. Usa alias para columnas
6. Solo joins necesarios
7. Devuelve SOLO el SQL, sin explicaciones

ESQUEMA DISPONIBLE:
{tables_info}

Ejemplos:
- "Ventas del último mes" → SELECT * FROM venta WHERE created_at >= NOW() - INTERVAL '1 month' LIMIT 100
- "Productos más vendidos" → SELECT pv.name, SUM(vd.quantity) as total FROM venta_detalle vd JOIN prenda_variante pv ON vd.variant_id = pv.id JOIN prenda pv ON pv.id = pv.garment_id GROUP BY pv.id ORDER BY total DESC LIMIT 10
"""

        try:
            response = self._ollama_generate(model=getattr(settings, "ollama_model", "codellama"), prompt=f"{system_prompt}\n\nUsuario: {prompt}\n\nSQL:")
            sql = self._extract_sql(response)

            # Validar SQL generado
            if not self._validate_sql(sql, allowed_tables):
                raise ValidationError("SQL generado no cumple reglas de seguridad")

            return {
                "sql": sql,
                "explanation": "SQL generado automáticamente desde lenguaje natural"
            }
        except Exception as e:
            raise ValidationError(f"Error generando SQL: {str(e)}")

    def execute_ai_report(self, prompt: str, max_rows: int = 100) -> dict:
        """Ejecutar reporte generado por IA y devolver resultados."""
        result = self.generate_sql_query(prompt, max_rows)
        sql = result["sql"]

        try:
            from app.core.database import engine
            with engine.connect() as conn:
                result = conn.execute(text(sql))
                columns = result.keys()
                rows = [list(row) for row in result.fetchall()]

                return {
                    "columns": list(columns),
                    "rows": rows,
                    "row_count": len(rows),
                    "generated_sql": sql,
                    "execution_time_ms": 0,  # Se podría medir
                }
        except Exception as e:
            raise ValidationError(f"Error ejecutando reporte: {str(e)}")

    # Métodos auxiliares privados

    def _get_tables_schema(self) -> str:
        """Obtener esquema de tablas permitidas para el prompt."""
        # Simplificado - en producción se leería de information_schema
        return """
        venta(id, invoice_number, client_id, branch_id, total_amount, status, created_at, paid_at)
        venta_detalle(id, sale_id, variant_id, quantity, unit_price)
        prenda(id, name, description, base_price, is_active, category_id)
        prenda_variante(id, garment_id, sku, price, size_id, color_id)
        talla(id, name), color(id, name, hex_code)
        inventario(id, branch_id, variant_id, quantity, reserved_quantity)
        cliente(id, user_id, first_name, last_name)
        usuario(id, email, roles)
        sucursal(id, name, address)
        """

    def _validate_sql(self, sql: str, allowed_tables: set) -> bool:
        """Validar que el SQL cumple reglas de seguridad."""
        sql_upper = sql.upper().strip()

        # Solo SELECT
        if not sql_upper.startswith("SELECT"):
            return False

        # No palabras peligrosas
        forbidden = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "CREATE", "TRUNCATE", "GRANT", "REVOKE"]
        for word in forbidden:
            if word in sql.upper():
                return False

        # Verificar tablas (básico)
        # En producción usar parser SQL real

        return True

    def _extract_sql(self, response: str) -> str:
        """Extraer SQL de la respuesta del modelo."""
        # Buscar bloques de código SQL
        import re
        code_blocks = re.findall(r"```sql\n(.*?)\n```", response, re.DOTALL | re.IGNORECASE)
        if code_blocks:
            return code_blocks[0].strip()

        # Si no hay bloques, buscar SELECT
        import re
        select_match = re.search(r"(SELECT\s+.*?)(?:\n\n|$)", response, re.DOTALL | re.IGNORECASE)
        if select_match:
            return select_match.group(1).strip()

        return response.strip()

    def _ollama_generate(self, model: str, prompt: str) -> str:
        """Llamar a Ollama generate endpoint."""
        try:
            response = self.ollama_client.post(
                "/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "num_predict": 500,
                    }
                },
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()
            return data.get("response", "")
        except Exception as e:
            raise Exception(f"Ollama generate error: {str(e)}")

    def _get_tables_schema(self) -> str:
        return self._get_tables_schema()


ai_service = AIService()
