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
    driver.get("https://graceful-living-web-application.onrender.com/");

    WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(5));

    // Wait for the link to be clickable, then click it
    wait.until(ExpectedConditions.elementToBeClickable(By.linkText("Shop"))).click();

    // Wait for the URL to contain "/shop" (or whatever your route is)
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

}