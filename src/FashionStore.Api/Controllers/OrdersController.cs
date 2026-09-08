using FashionStore.Api.DTOs;
using FashionStore.Core.Interfaces;
using FashionStore.Core.Specifications;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using System.Security.Claims;

namespace FashionStore.Api.Controllers;

[ApiController]
[Route("api/[controller]")]
[Authorize]
public class OrdersController : ControllerBase
{
    private readonly IOrderRepository _orderRepository;
    private readonly IUnitOfWork _unitOfWork;

    public OrdersController(IOrderRepository orderRepository, IUnitOfWork unitOfWork)
    {
        _orderRepository = orderRepository;
        _unitOfWork = unitOfWork;
    }

    [HttpGet]
    public async Task<ActionResult<IEnumerable<OrderDto>>> GetUserOrders([FromQuery] int page = 1, [FromQuery] int pageSize = 10)
    {
        var userId = User.FindFirstValue(ClaimTypes.NameIdentifier);
        var spec = new OrdersByUserSpecification(userId!, page, pageSize);
        var orders = await _orderRepository.ListAsync(spec);
        var totalCount = await _orderRepository.CountAsync(spec);

        var orderDtos = orders.Select(o => new OrderDto
        {
            Id = o.Id,
            OrderDate = o.OrderDate,
            Status = o.Status,
            Total = o.Total,
            ShippingAddress = o.ShippingAddress,
            ShippingCity = o.ShippingCity,
            PaymentMethod = o.PaymentMethod,
            Items = o.OrderItems.Select(oi => new OrderItemDto
            {
                Id = oi.Id,
                ProductId = oi.ProductId,
                ProductName = oi.Product?.Name ?? string.Empty,
                Quantity = oi.Quantity,
                UnitPrice = oi.UnitPrice,
                TotalPrice = oi.TotalPrice,
                SelectedSize = oi.SelectedSize,
                SelectedColor = oi.SelectedColor,
                ImageUrl = oi.Product?.ImageUrl
            }).ToList()
        });

        return Ok(new PagedResultDto<OrderDto>
        {
            Data = orderDtos,
            TotalCount = totalCount,
            Page = page,
            PageSize = pageSize
        });
    }

    [HttpGet("{id}")]
    public async Task<ActionResult<OrderDto>> GetOrder(int id)
    {
        var userId = User.FindFirstValue(ClaimTypes.NameIdentifier);
        var order = await _orderRepository.GetByIdAsync(id);
        
        if (order == null || order.UserId != userId)
            return NotFound();

        return Ok(new OrderDto
        {
            Id = order.Id,
            OrderDate = order.OrderDate,
            Status = order.Status,
            SubTotal = order.SubTotal,
            Tax = order.Tax,
            ShippingCost = order.ShippingCost,
            Discount = order.Discount,
            Total = order.Total,
            ShippingAddress = order.ShippingAddress,
            ShippingCity = order.ShippingCity,
            ShippingPostalCode = order.ShippingPostalCode,
            ShippingCountry = order.ShippingCountry,
            PaymentMethod = order.PaymentMethod,
            PaymentTransactionId = order.PaymentTransactionId,
            ShippedDate = order.ShippedDate,
            DeliveredDate = order.DeliveredDate,
            Items = order.OrderItems.Select(oi => new OrderItemDto
            {
                Id = oi.Id,
                ProductId = oi.ProductId,
                ProductName = oi.Product?.Name ?? string.Empty,
                Quantity = oi.Quantity,
                UnitPrice = oi.UnitPrice,
                TotalPrice = oi.TotalPrice,
                SelectedSize = oi.SelectedSize,
                SelectedColor = oi.SelectedColor,
                ImageUrl = oi.Product?.ImageUrl
            }).ToList()
        });
    }

    [HttpPost]
    public async Task<ActionResult<OrderDto>> CreateOrder(CreateOrderDto createOrderDto)
    {
        var userId = User.FindFirstValue(ClaimTypes.NameIdentifier);
        // Implementation would create order from cart items
        return Ok(new { message = "Order created successfully" });
    }

    [HttpPut("{id}/cancel")]
    public async Task<ActionResult> CancelOrder(int id)
    {
        var userId = User.FindFirstValue(ClaimTypes.NameIdentifier);
        var order = await _orderRepository.GetByIdAsync(id);
        
        if (order == null || order.UserId != userId)
            return NotFound();

        if (order.Status != "Pending" && order.Status != "Confirmed")
            return BadRequest("Order cannot be cancelled");

        order.Status = "Cancelled";
        await _unitOfWork.SaveChangesAsync();

        return Ok(new { message = "Order cancelled successfully" });
    }
}