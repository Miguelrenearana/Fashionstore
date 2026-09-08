using FashionStore.Core.Entities;
using Ardalis.Specification;

namespace FashionStore.Core.Interfaces;

public interface IOrderRepository : IRepositoryBase<Order>
{
    Task<Order?> GetOrderWithItemsAsync(int id);
    Task<IReadOnlyList<Order>> GetUserOrdersAsync(string userId, int page, int pageSize);
    Task<int> GetUserOrdersCountAsync(string userId);
}