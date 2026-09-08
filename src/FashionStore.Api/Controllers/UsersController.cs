using FashionStore.Api.DTOs;
using FashionStore.Core.Entities;
using FashionStore.Core.Interfaces;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Identity;
using Microsoft.AspNetCore.Mvc;

namespace FashionStore.Api.Controllers;

[ApiController]
[Route("api/[controller]")]
[Authorize]
public class UsersController : ControllerBase
{
    private readonly UserManager<User> _userManager;
    private readonly IOrderRepository _orderRepository;

    public UsersController(UserManager<User> userManager, IOrderRepository orderRepository)
    {
        _userManager = userManager;
        _orderRepository = orderRepository;
    }

    [HttpGet("addresses")]
    public async Task<ActionResult<IEnumerable<AddressDto>>> GetAddresses()
    {
        var userId = User.FindFirstValue(ClaimTypes.NameIdentifier);
        var user = await _userManager.FindByIdAsync(userId!);
        
        if (user == null)
            return NotFound();

        return Ok(new List<AddressDto>
        {
            new AddressDto
            {
                Id = 1,
                Type = "Shipping",
                FullName = $"{user.FirstName} {user.LastName}",
                Address = user.Address ?? string.Empty,
                City = user.City ?? string.Empty,
                PostalCode = user.PostalCode ?? string.Empty,
                Country = user.Country ?? string.Empty,
                PhoneNumber = user.PhoneNumber ?? string.Empty,
                IsDefault = true
            }
        });
    }

    [HttpPost("addresses")]
    public async Task<ActionResult<AddressDto>> AddAddress(CreateAddressDto createAddressDto)
    {
        return Ok(new AddressDto
        {
            Id = 1,
            Type = createAddressDto.Type,
            FullName = createAddressDto.FullName,
            Address = createAddressDto.Address,
            City = createAddressDto.City,
            PostalCode = createAddressDto.PostalCode,
            Country = createAddressDto.Country,
            PhoneNumber = createAddressDto.PhoneNumber,
            IsDefault = createAddressDto.IsDefault
        });
    }

    [HttpPut("addresses/{id}")]
    public async Task<ActionResult<AddressDto>> UpdateAddress(int id, UpdateAddressDto updateAddressDto)
    {
        return Ok(new AddressDto
        {
            Id = id,
            Type = updateAddressDto.Type,
            FullName = updateAddressDto.FullName,
            Address = updateAddressDto.Address,
            City = updateAddressDto.City,
            PostalCode = updateAddressDto.PostalCode,
            Country = updateAddressDto.Country,
            PhoneNumber = updateAddressDto.PhoneNumber,
            IsDefault = updateAddressDto.IsDefault
        });
    }

    [HttpDelete("addresses/{id}")]
    public async Task<ActionResult> DeleteAddress(int id)
    {
        return Ok(new { message = "Address deleted successfully" });
    }

    [HttpGet("wishlist")]
    public async Task<ActionResult<IEnumerable<ProductDto>>> GetWishlist()
    {
        return Ok(new List<ProductDto>());
    }

    [HttpPost("wishlist/{productId}")]
    public async Task<ActionResult> AddToWishlist(int productId)
    {
        return Ok(new { message = "Added to wishlist" });
    }

    [HttpDelete("wishlist/{productId}")]
    public async Task<ActionResult> RemoveFromWishlist(int productId)
    {
        return Ok(new { message = "Removed from wishlist" });
    }
}