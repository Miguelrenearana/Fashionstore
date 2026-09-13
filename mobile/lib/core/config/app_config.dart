/// API client configuration that can be overridden per environment.
class AppConfig {
  const AppConfig({
    this.apiBaseUrl = 'http://localhost:8000/api/v1',
    this.gateway = 'mock',
  });

  final String apiBaseUrl;
  final String gateway;

  static const AppConfig dev = AppConfig();
}