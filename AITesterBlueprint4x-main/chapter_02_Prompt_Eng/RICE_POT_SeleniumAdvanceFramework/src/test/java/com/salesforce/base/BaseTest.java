package com.salesforce.base;

import java.time.Duration;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;
import org.openqa.selenium.edge.EdgeDriver;
import org.openqa.selenium.firefox.FirefoxDriver;
import org.testng.annotations.AfterTest;
import org.testng.annotations.BeforeTest;

import com.salesforce.pages.LoginPage;
import com.salesforce.utils.ConfigReader;

import io.github.bonigarcia.wdm.WebDriverManager;

public class BaseTest {

    protected WebDriver driver;
    protected LoginPage loginPage;
    protected ConfigReader config;

    @BeforeTest
    public void setUp() {
        config = ConfigReader.getInstance();
        driver = initializeDriver(config.getProperty("browser"));
        driver.manage().window().maximize();
        driver.manage().timeouts().implicitlyWait(Duration.ofSeconds(config.getIntProperty("implicit.wait")));
        driver.get(config.getProperty("base.url"));
        loginPage = new LoginPage(driver);
    }

    @AfterTest
    public void tearDown() {
        try {
            if (driver != null) {
                driver.quit();
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private WebDriver initializeDriver(String browser) {
        switch (browser.toLowerCase()) {
            case "firefox":
                WebDriverManager.firefoxdriver().setup();
                return new FirefoxDriver();
            case "edge":
                WebDriverManager.edgedriver().setup();
                return new EdgeDriver();
            case "chrome":
            default:
                WebDriverManager.chromedriver().setup();
                ChromeOptions options = new ChromeOptions();
                if (config.getBoolProperty("headless")) {
                    options.addArguments("--headless=new", "--disable-gpu", "--window-size=1920,1080");
                }
                options.addArguments("--disable-notifications", "--remote-allow-origins=*");
                return new ChromeDriver(options);
        }
    }
}
