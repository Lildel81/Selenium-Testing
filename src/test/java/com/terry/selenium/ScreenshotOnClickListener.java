package com.terry.selenium;

import org.openqa.selenium.*;
import org.openqa.selenium.support.events.WebDriverListener;

import java.io.File;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

public class ScreenshotOnClickListener implements WebDriverListener {

    
    public void afterClick(WebElement element, WebDriver driver) {
        try {
            takeScreenshot(driver, element);
        } catch (Exception e) {
            // Don't fail the test just because screenshot failed
            e.printStackTrace();
        }
    }

    private void takeScreenshot(WebDriver driver, WebElement element) throws Exception {
        String timestamp = LocalDateTime.now()
                .format(DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss_SSS"));

        String label = safeLabel(element);

        File src = ((TakesScreenshot) driver).getScreenshotAs(OutputType.FILE);
        Path dest = Path.of("screenshots", "click_" + label + "_" + timestamp + ".png");

        Files.createDirectories(dest.getParent());
        Files.copy(src.toPath(), dest);
        System.out.println("📸 Saved screenshot to: " + dest.toAbsolutePath());
    }

    private String safeLabel(WebElement element) {
        try {
            String text = element.getText();
            if (text == null || text.isBlank()) {
                text = element.getTagName();
            }
            // make it filesystem-safe
            return text.replaceAll("[^a-zA-Z0-9_-]", "_");
        } catch (Exception e) {
            return "element";
        }
    }
}
