using FashionStore.Core.Entities;
using FashionStore.Core.Interfaces;
using FashionStore.Infrastructure.Data;
using Ardalis.Specification.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore;

namespace FashionStore.Infrastructure.Repositories;

public class ProductRepository : RepositoryBase<Product>, IProductRepository
{
    private readonly AppDbContext _context;

    public ProductRepository(AppDbContext context) : base(context)
    {
        _context = context;
    }

    public async Task<Product?> GetProductWithCategoryAsync(int id)
    {
        return await _context.Products
            .Include(p => p.Category)
            .FirstOrDefaultAsync(p => p.Id == id);
    }

    public async Task<IReadOnlyList<Product>> GetFeaturedProductsAsync(int count)
    {
        return await _context.Products
            .Include(p => p.Category)
            .Where(p => p.IsActive && p.IsFeatured && p.StockQuantity > 0)
            .OrderByDescending(p => p.CreatedAt)
            .Take(count)
            .ToListAsync();
    }

    public async Task<int> GetTotalCountAsync(ISpecification<Product> spec)
    {
        return await ApplySpecification(spec).CountAsync();
    }
}