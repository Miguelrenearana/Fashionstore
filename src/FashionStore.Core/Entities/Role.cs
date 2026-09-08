using Microsoft.AspNetCore.Identity;

namespace FashionStore.Core.Entities;

public class Role : IdentityRole<int>
{
    public string? Description { get; set; }
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}