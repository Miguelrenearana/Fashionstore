using FashionStore.Core.Entities;
using Ardalis.Specification;

namespace FashionStore.Core.Interfaces;

public interface ICategoryRepository : IRepositoryBase<Category>
{
    Task<Category?> GetCategoryWithProductsAsync(int id);
    Task<IReadOnlyList<Category>> GetRootCategoriesAsync();
    Task<IReadOnlyList<Product>> GetProductsAsync(ISpecification<Product> spec);
    Task<int> CountProductsAsync(ISpecification<Product> spec);
}