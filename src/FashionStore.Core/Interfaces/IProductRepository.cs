using FashionStore.Core.Entities;
using Ardalis.Specification;

namespace FashionStore.Core.Interfaces;

public interface IProductRepository : IRepositoryBase<Product>
{
    Task<Product?> GetProductWithCategoryAsync(int id);
    Task<IReadOnlyList<Product>> GetFeaturedProductsAsync(int count);
    Task<int> GetTotalCountAsync(ISpecification<Product> spec);
}