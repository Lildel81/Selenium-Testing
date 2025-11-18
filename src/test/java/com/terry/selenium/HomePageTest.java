package com.terry.selenium;


import io.github.bonigarcia.wdm.WebDriverManager;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Assertions;
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.support.ui.WebDriverWait;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.WebElement;

import java.time.Duration;
import java.util.function.Function;

public class HomePageTest {

    private WebDriver driver;

    @BeforeEach
    public void setUp() {
        WebDriverManager.chromedriver().setup();
        driver = new ChromeDriver();
    }

    @AfterEach
    public void tearDown() {
        if (driver != null) {
            driver.quit();
        }
    }

    @Test
    public void testHomePageTitle() {
        System.out.println("Testing the homepage title is GracefuLiving");
       driver.get("https://graceful-living-web-application.onrender.com/");

       String title =   driver.getTitle();

       System.out.println("Page Title: " + title);

       Assertions.assertFalse(title.isBlank(), "Page Title should not be blank");

       Assertions.assertEquals("GracefuLiving", title);
   }

 @Test
void clickingShopLinkNavigatesToShopPage() {
    System.out.println("Testing the Shop link takes us to the shop");

    //set where we want to go
    driver.get("https://graceful-living-web-application.onrender.com/");

    //set how long want to wait for the link to appear
    WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(5));

    // Wait for the link to be clickable, then click it
    wait.until(ExpectedConditions.elementToBeClickable(By.linkText("Shop"))).click();

    // Wait for the URL to contain "/shop"
    wait.until(ExpectedConditions.urlContains("/shop"));

    // Assert we really navigated there
    String currentUrl = driver.getCurrentUrl();
    Assertions.assertTrue(currentUrl.contains("/shop"),
            "Expected URL to contain /shop but was: " + currentUrl);
}

@Test
void optionToAddYogaToCart(){
    System.out.println("Tessting the Yoga card takes us to the add to cart page");
    driver.get("https://graceful-living-web-application.onrender.com/shop");

    WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(5));

 
    wait.until(ExpectedConditions.elementToBeClickable(By.className("gl-shop-card"))).click();

 
   wait.until(ExpectedConditions.urlContains("/yoga"));
   String currentUrl = driver.getCurrentUrl();
   Assertions.assertTrue(currentUrl.contains("/yoga"), "Expected URL to contain /yoga but was: " + currentUrl);

   
}


@Test
void addingProductShowsItInCart(){
    driver.get("https://graceful-living-web-application.onrender.com/shop/yoga");

    WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(5));

    wait.until(ExpectedConditions.elementToBeClickable(By.xpath("//button[normalize-space(text())='Add to Cart']"))
).click();

    wait.until(ExpectedConditions.urlContains("/cart"));
    String currentUrl = driver.getCurrentUrl();
    Assertions.assertTrue(currentUrl.contains("/cart"), "Expected URL to conatin /cart but was: " + currentUrl);


}

@Test
void yogaLessonsQuantityIncreasesWhenAddedAgain() {
    System.out.println("Testing the add to cart button actually adds it to the cart");
    driver.get("https://graceful-living-web-application.onrender.com/cart");
     WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(5));

    By yogaQuantityLocator = By.xpath("//tr[td[normalize-space()='Yoga Lessons']]/td[2]");

     int before;
    try {
        WebElement quantityCellBefore = wait.until(ExpectedConditions.visibilityOfElementLocated(yogaQuantityLocator));
        before = Integer.parseInt(quantityCellBefore.getText().trim());
    } catch (org.openqa.selenium.TimeoutException e) {
      
        before = 0;

    }
    System.out.println("Before: " + before);

    

  
    driver.get("https://graceful-living-web-application.onrender.com/shop/yoga");
   
    By addToCartButtonLocator = By.xpath("//button[normalize-space(text())='Add to Cart']");



    WebElement addToCartButton = wait.until(
            ExpectedConditions.elementToBeClickable(addToCartButtonLocator)
    );
    addToCartButton.click();

   
    driver.get("https://graceful-living-web-application.onrender.com/cart");

   
    WebElement quantityCellAfter = driver.findElement(yogaQuantityLocator);
    int after = Integer.parseInt(quantityCellAfter.getText().trim());

  
    Assertions.assertEquals(before + 1, after,
        "Expected Yoga Lessons quantity to increase by 1");
}


@Test
void logIntoAdminPortal(){
    System.out.println("Logging into the admin portal");
    driver.get("https://graceful-living-web-application.onrender.com/");

    WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(5));


    WebElement loginLink = wait.until(ExpectedConditions.elementToBeClickable(By.className("btn")));
    loginLink.click();

    WebElement adminLogin = wait.until(ExpectedConditions.elementToBeClickable(By.linkText("Admin Login")));
    adminLogin.click();

    WebElement usernameField = wait.until(ExpectedConditions.visibilityOfElementLocated(By.className("username-box")));
    usernameField.sendKeys("terry");

    

    WebElement passwordField = wait.until(ExpectedConditions.visibilityOfElementLocated(By.className("password-box")));
    passwordField.sendKeys("changeme");

    WebElement loginButton = wait.until(ExpectedConditions.elementToBeClickable(By.className("login_button")));
    loginButton.click();
    wait.until(ExpectedConditions.urlContains("/admin"));
    String currentUrl = driver.getCurrentUrl();

    Assertions.assertTrue(currentUrl.contains("/admin"), 
        "Expected URL to contain /admin but was: " + currentUrl);

}

@Test
void testShopManagmentLink(){

    System.out.println("Tsesting the shop management link in admin portal");
    driver.get("https://graceful-living-web-application.onrender.com/");

    WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(5));


    WebElement loginLink = wait.until(ExpectedConditions.elementToBeClickable(By.className("btn")));
    loginLink.click();

    WebElement adminLogin = wait.until(ExpectedConditions.elementToBeClickable(By.linkText("Admin Login")));
    adminLogin.click();

    WebElement usernameField = wait.until(ExpectedConditions.visibilityOfElementLocated(By.className("username-box")));
    usernameField.sendKeys("terry");

    

    WebElement passwordField = wait.until(ExpectedConditions.visibilityOfElementLocated(By.className("password-box")));
    passwordField.sendKeys("changeme");

    WebElement loginButton = wait.until(ExpectedConditions.elementToBeClickable(By.className("login_button")));
    loginButton.click();

    WebElement shopManagementLink = wait.until(ExpectedConditions.elementToBeClickable(By.linkText("Shop Management")));
    shopManagementLink.click();

    wait.until(ExpectedConditions.urlContains("/shop/admin/list"));
    String currentUrl = driver.getCurrentUrl();
    Assertions.assertTrue(currentUrl.contains("/shop/admin/list"),
        "Expected URL to contain /shop/admin/list but was: " + currentUrl);
}

}