using FashionStore.Core.Entities;
using FashionStore.Core.Interfaces;
using FashionStore.Infrastructure.Data;
using Ardalis.Specification.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore;

namespace FashionStore.Infrastructure.Repositories;

public class CategoryRepository : RepositoryBase<Category>, ICategoryRepository
{
    private readonly AppDbContext _context;

    public CategoryRepository(AppDbContext context) : base(context)
    {
        _context = context;
    }

    public async Task<Category?> GetCategoryWithProductsAsync(int id)
    {
        return await _context.Categories
            .Include(c => c.Products)
            .FirstOrDefaultAsync(c => c.Id == id);
    }

    public async Task<IReadOnlyList<Category>> GetRootCategoriesAsync()
    {
        return await _context.Categories
            .Where(c => c.ParentCategoryId == null && c.IsActive)
            .OrderBy(c => c.DisplayOrder)
            .ToListAsync();
    }

    public async Task<IReadOnlyList<Product>> GetProductsAsync(ISpecification<Product> spec)
    {
        return await ApplySpecification(spec).ToListAsync();
    }

    public async Task<int> CountProductsAsync(ISpecification<Product> spec)
    {
        return await ApplySpecification(spec).CountAsync();
    }
}