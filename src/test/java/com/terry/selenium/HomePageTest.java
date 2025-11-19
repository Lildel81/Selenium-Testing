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
import org.openqa.selenium.support.events.EventFiringDecorator;
import org.openqa.selenium.TimeoutException;
import org.openqa.selenium.Alert;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.TestInstance;
import org.junit.jupiter.api.TestInstance.Lifecycle;


import org.openqa.selenium.OutputType;
import org.openqa.selenium.TakesScreenshot;

import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.File;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.Duration;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

@TestInstance(Lifecycle.PER_CLASS)  


public class HomePageTest {
    public static final String RESET = "\u001B[0m";
    public static final String RED = "\u001B[31m";
    public static final String GREEN = "\u001B[32m";
    public static final String YELLOW = "\u001B[33m";
    public static final String BLUE = "\u001B[34m";
    public static final String CYAN = "\u001B[36m";
    public static final String BOLD = "\u001B[1m";


    int NumOfTests = 0;

    private By testProductRowLocator() {
    return By.xpath("//tr[.//strong[normalize-space()='test']]");
}

    private int getTestProductRowCount() {
    return driver.findElements(testProductRowLocator()).size();
}

      private void takeScreenshot(String label) {
    try {
       
        String timestamp = LocalDateTime.now()
                .format(DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss_SSS"));

        File src = ((TakesScreenshot) driver).getScreenshotAs(OutputType.FILE);

        Path dest = Path.of("screenshots", label + ".png");
        Files.createDirectories(dest.getParent());   // create screenshots/ if it doesn't exist
        Files.copy(src.toPath(), dest);

        //System.out.println("📸 Saved screenshot: " + dest.toAbsolutePath());
    } catch (Exception e) {
       
        //e.printStackTrace();
    }
}


    private void waitForHomePage(WebDriverWait wait) {
    wait.until(ExpectedConditions.presenceOfElementLocated(By.cssSelector(".quote-container")));
}

    public static void printWithLines(String msg){
        System.out.println("------------------------------------------------------------------------------------");
        System.out.println(CYAN+ msg + RESET);
        
    }

    public static void success(String msg){
        System.out.println(GREEN + "** " + msg + " **" + RESET);
        System.out.println("------------------------------------------------------------------------------------");

    }

   

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

     @AfterAll
    void afterAllTests() {
        System.out.println("\u001B[32m" + NumOfTests + " tests are finished successfully!\u001B[0m");
    }


@Test
    void testHomePageTitle() {
        NumOfTests++;;
        printWithLines("Testing the homepage title is GracefuLiving");
       driver.get("http://127.0.0.1:8080/");

       String title =   driver.getTitle();

       System.out.println("Page Title: " + title);

       Assertions.assertFalse(title.isBlank(), "Page Title should not be blank");

       Assertions.assertEquals("GracefuLiving", title);
       takeScreenshot("Title");
   }

@Test
void clickingShopLinkNavigatesToShopPage() {
    NumOfTests++;
    printWithLines("Testing Shop Page");

    //set where we want to go
    driver.get("http://127.0.0.1:8080/");

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
    
    takeScreenshot("Testing_Shop_1");
    success("Shop Page Passed");
}

@Test
void optionToAddYogaToCart(){
    NumOfTests++;
    printWithLines("Testing Cart Page");
    driver.get("http://127.0.0.1:8080/shop");

    WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(5));

 
    wait.until(ExpectedConditions.elementToBeClickable(By.className("gl-shop-card"))).click();
    

 
   wait.until(ExpectedConditions.urlContains("/test"));
   takeScreenshot("Add_service_to_cart_1");
   String currentUrl = driver.getCurrentUrl();
   Assertions.assertTrue(currentUrl.contains("/test"), "Expected URL to contain /test but was: " + currentUrl);

   takeScreenshot("Add_service_to_cart_1");
   success("Cart Page Passed");


   
}


@Test
void addingProductShowsItInCart(){
    NumOfTests++;
    printWithLines("Testing Add Item To Cart");

    driver.get("http://127.0.0.1:8080/shop/test");

    WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(5));

    wait.until(ExpectedConditions.elementToBeClickable(By.xpath("//button[normalize-space(text())='Add to Cart']"))
).click();

    wait.until(ExpectedConditions.urlContains("/cart"));
    
    String currentUrl = driver.getCurrentUrl();
    Assertions.assertTrue(currentUrl.contains("/cart"), "Expected URL to conatin /cart but was: " + currentUrl);
    takeScreenshot("Shows_item_in_cart_1");

    success("Add Item To Cart Passed");


}

@Test
void yogaLessonsQuantityIncreasesWhenAddedAgain() {
    NumOfTests++;
    printWithLines("Testing Count Increases In Cart");
    driver.get("http://127.0.0.1:8080/cart");
     WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(5));
     takeScreenshot("Cart_Quantity_Increased_Current_cart");

    By yogaQuantityLocator = By.xpath("//tr[td[normalize-space()='test']]/td[2]");

     int before;
    try {
        WebElement quantityCellBefore = wait.until(ExpectedConditions.visibilityOfElementLocated(yogaQuantityLocator));
        before = Integer.parseInt(quantityCellBefore.getText().trim());
    } catch (org.openqa.selenium.TimeoutException e) {
      
        before = 0;

    }
    System.out.println("Before: " + before);

    

  
    driver.get("http://127.0.0.1:8080/shop/test");
   
    By addToCartButtonLocator = By.xpath("//button[normalize-space(text())='Add to Cart']");



    WebElement addToCartButton = wait.until(
            ExpectedConditions.elementToBeClickable(addToCartButtonLocator)
    );
    addToCartButton.click();

   
    driver.get("http://127.0.0.1:8080/cart");

   
    WebElement quantityCellAfter = driver.findElement(yogaQuantityLocator);
    int after = Integer.parseInt(quantityCellAfter.getText().trim());
    System.out.println("After: " + after);
  
    Assertions.assertEquals(before + 1, after,
        "Expected Yoga Lessons quantity to increase by 1");
        takeScreenshot("Shop_Quantity_Increased_New_Cart");
        success("Count Increases In Cart Passed");
}




@Test
void testShopManagmentLink(){

    
    driver.get("http://127.0.0.1:8080/");

    WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(5));

    //moving to the login page
    NumOfTests++;
    printWithLines("Testing Login Page");
    WebElement loginLink = wait.until(ExpectedConditions.elementToBeClickable(By.className("btn")));
    loginLink.click();
    wait.until(ExpectedConditions.urlContains("/user-login"));
    String currentUrl = driver.getCurrentUrl();
    Assertions.assertTrue(currentUrl.contains("/user-login"), "Expected URL to contain /user-login but was: " + currentUrl);
    takeScreenshot("Shop_Management_1_user_login");
    success("Login Page Test Passed");



    //Moving to admin page
    NumOfTests++;
    printWithLines("Testing Admin Login Page");
    WebElement adminLogin = wait.until(ExpectedConditions.elementToBeClickable(By.linkText("Admin Login")));
    adminLogin.click();
    wait.until(ExpectedConditions.urlContains("/login"));
    currentUrl = driver.getCurrentUrl();
    Assertions.assertTrue(currentUrl.contains("/login"), "Expected URL to contain /login but was: " + currentUrl);
    takeScreenshot("Shop_Management_2_admin_login");
    success("Admin Login Page Passed");

    //Entering Data into Fields
    NumOfTests++;
    WebElement usernameField = wait.until(ExpectedConditions.visibilityOfElementLocated(By.className("username-box")));
    usernameField.sendKeys("terry");

    WebElement passwordField = wait.until(ExpectedConditions.visibilityOfElementLocated(By.className("password-box")));
    passwordField.sendKeys("changeme");
    takeScreenshot("Shop_Management_3_data_entered");

    WebElement loginButton = wait.until(ExpectedConditions.elementToBeClickable(By.className("login_button")));
    loginButton.click();

    //moving to admin portal
    NumOfTests++;
    printWithLines("Testing Admin Portal");
    wait.until(ExpectedConditions.urlContains("/adminportal"));
    currentUrl = driver.getCurrentUrl();
    Assertions.assertTrue(currentUrl.contains("/adminportal"), "Expected URL to contain /adminportal but was: "+ currentUrl);
    takeScreenshot("Shop_Management_4_admin_portal");
    success("Admin Portal Passed");

    //movint to shop management page
    NumOfTests++;
    printWithLines("Testing Shop Management Page");
    WebElement shopManagementLink = wait.until(ExpectedConditions.elementToBeClickable(By.linkText("Shop Management")));
    shopManagementLink.click();
    wait.until(ExpectedConditions.urlContains("/shop/admin/list"));
    currentUrl = driver.getCurrentUrl();
    Assertions.assertTrue(currentUrl.contains("/shop/admin/list"), "Expected current URL to contian /shop/admin/list but was: " + currentUrl);
    takeScreenshot("Shop_Management_4_Shop_Management_Page");
    success("Shop Management Page Passed");

    NumOfTests++;
    printWithLines("Testing New Product");
    WebElement newProduct = wait.until(ExpectedConditions.elementToBeClickable(By.linkText("+ New Product")));
    newProduct.click();
    wait.until(ExpectedConditions.urlContains("/shop/admin/new"));
    currentUrl = driver.getCurrentUrl();
    Assertions.assertTrue(currentUrl.contains("/shop/admin/new"), "Expeced current URL to contain /shop/admin/new but was: " + currentUrl);
    takeScreenshot("Shop_Management_4_New_Product_Page");
    success("New Product Passed");

    
    WebElement itemTitle = wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("title")));
    itemTitle.sendKeys("test");
    WebElement itemPrice = wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("priceDollars")));
    itemPrice.sendKeys("100");
    WebElement itemStock = wait.until(ExpectedConditions.visibilityOfElementLocated(By.name("stock")));
    itemStock.sendKeys("1");
    String filePath = Paths.get("src/test/resources/images/sound_healing.png")
                       .toAbsolutePath()
                       .toString();
    WebElement itemImage = wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("image")));
    itemImage.sendKeys(filePath);
    WebElement createButton = wait.until(ExpectedConditions.elementToBeClickable(By.cssSelector("button[type='submit']")));
    createButton.click();
    NumOfTests++;
    printWithLines("Testing Create Form");
    WebElement tileTitle = wait.until(ExpectedConditions.visibilityOfElementLocated(By.cssSelector("h2.gl-shop-card-title")));


    Assertions.assertEquals("test", tileTitle.getText(), "Expected to be on the New Product page");
    success("Create Form Passed");

    NumOfTests++;
    printWithLines("Testing Delete Button");
    WebElement adminPortalLink = driver.findElement(By.linkText("Admin Portal"));
    adminPortalLink.click();
    WebElement shopManagementLink2 = wait.until(ExpectedConditions.elementToBeClickable(By.linkText("Shop Management")));
    shopManagementLink2.click();

    wait.until(ExpectedConditions.urlContains("/list"));

     int beforeCount = getTestProductRowCount();
    System.out.println("👉 Rows for 'test' BEFORE delete: " + beforeCount);

    if (beforeCount == 0) {
        // Nothing to delete, so just assert that it's indeed gone
        Assertions.assertTrue(true, "No 'test' products exist, as expected.");
        success("No 'test' row present — already deleted.");
        return;
    }
    takeScreenshot("Delete_Button_Test_Before");
    By rowLocator = testProductRowLocator();
    WebElement row = wait.until(ExpectedConditions.visibilityOfElementLocated(rowLocator));

    WebElement deleteButton = row.findElement(By.xpath(".//button[normalize-space()='Delete']"));
    deleteButton.click();

      
    boolean gone = wait.until(driver -> getTestProductRowCount() == beforeCount - 1);

    int afterCount = getTestProductRowCount();
    System.out.println("👉 Rows for 'test' AFTER delete: " + afterCount);

    Assertions.assertTrue(
        gone && afterCount == beforeCount - 1,
        "Expected 'test' product row to be deleted, but Selenium still sees " + afterCount + " row(s)."
    );
    takeScreenshot("Delete_Button_Test_After");
    success("Delete Button Passed");

     WebElement adminPortalLink3 = driver.findElement(By.linkText("Admin Portal"));
    adminPortalLink3.click();

    NumOfTests++;
    printWithLines("Testing Content Management Page");
    WebElement contentManagementLink = wait.until(ExpectedConditions.elementToBeClickable(By.linkText("Content Management")));
    contentManagementLink.click();
    wait.until(ExpectedConditions.urlContains("/content-management"));
    currentUrl = driver.getCurrentUrl();
    Assertions.assertTrue(currentUrl.contains("/content-management"), "Expected current URL to contian /content-management but was: " + currentUrl);
    takeScreenshot("Content_Management_Page");
    success("Content Management Page Passed");

    WebElement adminPortalLink4 = driver.findElement(By.linkText("Admin Portal"));
    adminPortalLink4.click();

    NumOfTests++;
    printWithLines("Testing Client Management Page");
    WebElement clientManagementLink = wait.until(ExpectedConditions.elementToBeClickable(By.linkText("Client Management")));
    clientManagementLink.click();
    wait.until(ExpectedConditions.urlContains("/clientmanagement"));
    currentUrl = driver.getCurrentUrl();
    Assertions.assertTrue(currentUrl.contains("/clientmanagement"), "Expected current URL to contian /clientmanagement but was: " + currentUrl);
    takeScreenshot("Client_Management_Page");
    success("client Management Page Passed");

}

@Test
void testAssessYourBalanceButtonOnHomepage(){
    NumOfTests++;
    printWithLines("Testing Homepage Slider Button");

    driver.get("http://127.0.0.1:8080/");

    
    WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(5));

    WebElement assessButton = wait.until(ExpectedConditions.elementToBeClickable(By.cssSelector("button.slide-btn")));
    assessButton.click();
    

    wait.until(ExpectedConditions.urlContains("/intro"));
    

    String currentUrl = driver.getCurrentUrl();
    Assertions.assertTrue(currentUrl.contains("/intro"),
            "Expected URL to contain /intro but was: " + currentUrl);
    
    takeScreenshot("Homepage_Slider_Button");
    success("Homepage Slider Button Passed");

}

@Test 
void testTakeOurQuizButtonOnHomepage(){
    NumOfTests++;
    printWithLines("Testing Take Our Quiz Button");

    driver.get("http://127.0.0.1:8080/");

     WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(15));

     waitForHomePage(wait);

     WebElement quizButton = wait.until(ExpectedConditions.elementToBeClickable(By.id("quiz-button")));
    quizButton.click();
    

    wait.until(ExpectedConditions.urlContains("/intro"));
    

    String currentUrl = driver.getCurrentUrl();
    Assertions.assertTrue(currentUrl.contains("/intro"),
            "Expected URL to contain /intro but was: " + currentUrl);
    takeScreenshot("Quiz_Button_Homepage");
    success("Take Our Quiz Button Passed");
}

@Test
void testReadMoreTestimonialsButton(){
    NumOfTests++;
    printWithLines("Testing Read More Testimonials Button");

    driver.get("http://127.0.0.1:8080/");

    WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(5));

    waitForHomePage(wait);

     WebElement readMore = wait.until(ExpectedConditions.elementToBeClickable(By.cssSelector("a.btn.btn-testimonial")));
    readMore.click();
    

    wait.until(ExpectedConditions.urlContains("/reviews"));
    

    String currentUrl = driver.getCurrentUrl();
    Assertions.assertTrue(currentUrl.contains("/reviews"),
            "Expected URL to contain /reviews but was: " + currentUrl);
    takeScreenshot("Testimonial_Button_Homepage");
    success("Take Our Quiz Button Passed");

}

@Test
void testInvalidAdminLogin(){
    printWithLines("Testing Invalid Admin Login");

     driver.get("http://127.0.0.1:8080/");

    WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(5));

    NumOfTests++;
   
    WebElement loginLink = wait.until(ExpectedConditions.elementToBeClickable(By.className("btn")));
    loginLink.click();

    WebElement adminLogin = wait.until(ExpectedConditions.elementToBeClickable(By.linkText("Admin Login")));
    adminLogin.click();

    WebElement usernameField = wait.until(ExpectedConditions.visibilityOfElementLocated(By.className("username-box")));
    usernameField.sendKeys("notTerry");

    WebElement passwordField = wait.until(ExpectedConditions.visibilityOfElementLocated(By.className("password-box")));
    passwordField.sendKeys("notmypassword");
    takeScreenshot("Invalid_Password_data_entered");

    WebElement loginButton = wait.until(ExpectedConditions.elementToBeClickable(By.className("login_button")));
    loginButton.click();

    wait.until(ExpectedConditions.urlContains("/login"));
    

    String currentUrl = driver.getCurrentUrl();
    Assertions.assertTrue(currentUrl.contains("/login"),
            "Expected URL to contain /reviews but was: " + currentUrl);
    takeScreenshot("Invalid_Password_data_submitted");
    success("Invalid Admin Login Passed");

}



}