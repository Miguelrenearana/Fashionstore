using FashionStore.Api.DTOs;
using FashionStore.Core.Interfaces;
using FashionStore.Core.Specifications;
using Microsoft.AspNetCore.Mvc;

namespace FashionStore.Api.Controllers;

[ApiController]
[Route("api/[controller]")]
public class CategoriesController : ControllerBase
{
    private readonly ICategoryRepository _categoryRepository;

    public CategoriesController(ICategoryRepository categoryRepository)
    {
        _categoryRepository = categoryRepository;
    }

    [HttpGet]
    public async Task<ActionResult<IEnumerable<CategoryDto>>> GetCategories([FromQuery] bool includeInactive = false)
    {
        var spec = new CategoriesSpecification(includeInactive);
        var categories = await _categoryRepository.ListAsync(spec);

        var categoryDtos = categories.Select(c => new CategoryDto
        {
            Id = c.Id,
            Name = c.Name,
            Description = c.Description,
            Slug = c.Slug,
            ImageUrl = c.ImageUrl,
            ParentCategoryId = c.ParentCategoryId,
            IsActive = c.IsActive,
            DisplayOrder = c.DisplayOrder,
            SubCategories = c.SubCategories?.Select(sc => new CategoryDto
            {
                Id = sc.Id,
                Name = sc.Name,
                Description = sc.Description,
                Slug = sc.Slug,
                ImageUrl = sc.ImageUrl,
                ParentCategoryId = sc.ParentCategoryId,
                IsActive = sc.IsActive,
                DisplayOrder = sc.DisplayOrder
            }).ToList() ?? new List<CategoryDto>()
        });

        return Ok(categoryDtos);
    }

    [HttpGet("{id}")]
    public async Task<ActionResult<CategoryDto>> GetCategory(int id)
    {
        var category = await _categoryRepository.GetByIdAsync(id);
        if (category == null)
            return NotFound();

        return Ok(new CategoryDto
        {
            Id = category.Id,
            Name = category.Name,
            Description = category.Description,
            Slug = category.Slug,
            ImageUrl = category.ImageUrl,
            ParentCategoryId = category.ParentCategoryId,
            IsActive = category.IsActive,
            DisplayOrder = category.DisplayOrder
        });
    }

    [HttpGet("{id}/products")]
    public async Task<ActionResult<IEnumerable<ProductDto>>> GetCategoryProducts(int id, [FromQuery] int page = 1, [FromQuery] int pageSize = 12)
    {
        var spec = new ProductsByCategorySpecification(id, page, pageSize);
        var products = await _categoryRepository.GetProductsAsync(spec);
        var totalCount = await _categoryRepository.CountProductsAsync(spec);

        var productDtos = products.Select(p => new ProductDto
        {
            Id = p.Id,
            Name = p.Name,
            Description = p.Description,
            Price = p.Price,
            DiscountPrice = p.DiscountPrice,
            ImageUrl = p.ImageUrl,
            IsFeatured = p.IsFeatured,
            CategoryId = p.CategoryId,
            CategoryName = p.Category?.Name,
            InStock = p.StockQuantity > 0
        });

        return Ok(new PagedResultDto<ProductDto>
        {
            Data = productDtos,
            TotalCount = totalCount,
            Page = page,
            PageSize = pageSize
        });
    }
}