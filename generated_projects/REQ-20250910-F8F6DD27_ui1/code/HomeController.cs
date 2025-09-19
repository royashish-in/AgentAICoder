using Microsoft.AspNetCore.Mvc;
using System.Threading.Tasks;
using Serilog;
using Microsoft.EntityFrameworkCore;

namespace MyApi.Controllers
{
    public class HomeController : Controller
    {
        private readonly ILogger _logger;
        private readonly MyDbContext _dbContext;

        public HomeController(ILogger<HomeController> logger, MyDbContext dbContext)
        {
            _logger = logger;
            _dbContext = dbContext;
        }

        [HttpGet]
        [Authorize]
        public async Task<IActionResult> Index()
        {
            try
            {
                var result = await DoSomethingAsync();
                return Ok(result);
            }
            catch (TimeoutException ex) when (ex is TimeoutException || ex is OperationCanceledException)
            {
                _logger.LogError(ex, "Request timed out or operation cancelled in Index method");
                return StatusCode(408, "Request Timed Out");
            }
            catch (InvalidOperationException ex) when (ex != null && !string.IsNullOrEmpty(ex.Message))
            {
                if (ex.Message.Contains("User not found"))
                {
                    _logger.LogError(ex, "Invalid operation in DoSomethingAsync method - User not found: {User}", string.Empty);
                    return StatusCode(404, "Not Found");
                }
                else
                {
                    _logger.LogError(ex, "Invalid operation in DoSomethingAsync method with details: {Details}", ex.Message);
                    return StatusCode(500, "Internal Server Error");
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error in Index method with details: {Details}", GetErrorDetails(ex));
                return StatusCode(500, "Internal Server Error");
            }
        }

        private async Task<string> DoSomethingAsync()
        {
            try
            {
                using var dbContext = new MyDbContext();
                dbContext.Database.Connection.Open();

                var user = await _dbContext.Users
                    .Include(u => u.Orders)
                    .FirstOrDefaultAsync(u => u.Id == 1);

                if (user != null)
                {
                    // Perform operations on the user object
                }
                else
                {
                    throw new InvalidOperationException("User not found");
                }

                dbContext.Database.Connection.Close();

                return "Operation successful";
            }
            catch (Exception ex) when (ex is DbUpdateException || ex is DbUpdateConcurrencyException)
            {
                _logger.LogError(ex, "Error updating database in DoSomethingAsync method with details: {Details}", GetErrorDetails(ex));
                throw;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error in DoSomethingAsync method with details: {Details}", GetErrorDetails(ex));
                return string.Empty;
            }
        }

        private string GetErrorDetails(Exception exception)
        {
            if (exception is DbUpdateException dbEx || exception is DbUpdateConcurrencyException dbConcEx)
            {
                var sqlException = dbEx as SqlException ?? dbConcEx as SqlException;
                if (sqlException != null && !string.IsNullOrEmpty(sqlException.Message))
                {
                    return $"SQL error: {sqlException.Message}";
                }
            }

            return exception.ToString();
        }
    }
}

// MyDbContext.cs
public class MyDbContext : DbContext
{
    public DbSet<User> Users { get; set; }
    public DbSet<Order> Orders { get; set; }

    protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
    {
        optionsBuilder.UseSqlServer("Server=myserver;Database=mydatabase;User Id=myuser;Password=mypassword;");
    }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<User>().ToTable("Users");
        modelBuilder.Entity<Order>().ToTable("Orders");

        modelBuilder.Entity<User>()
            .HasMany(u => u.Orders)
            .WithOne(o => o.User)
            .HasForeignKey(o => o.UserId);
    }
}