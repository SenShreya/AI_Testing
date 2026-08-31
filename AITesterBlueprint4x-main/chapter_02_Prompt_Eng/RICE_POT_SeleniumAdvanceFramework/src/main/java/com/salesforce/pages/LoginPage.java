package com.salesforce.pages;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.FindBy;
import org.openqa.selenium.support.PageFactory;

import com.salesforce.utils.ConfigReader;
import com.salesforce.utils.WaitUtils;

public class LoginPage {

    private final WebDriver driver;
    private final WaitUtils wait;
    private final ConfigReader config;

    @FindBy(xpath = "//input[@id='username']")
    private WebElement usernameField;

    @FindBy(xpath = "//input[@id='password']")
    private WebElement passwordField;

    @FindBy(xpath = "//button[contains(text(),'Log In')]")
    private WebElement loginButton;

    @FindBy(xpath = "//input[@type='checkbox']")
    private WebElement rememberMeCheckbox;

    @FindBy(xpath = "//div[@id='error']")
    private WebElement errorMessage;

    @FindBy(xpath = "//a[contains(text(),'Forgot Your Password')]")
    private WebElement forgotPasswordLink;

    @FindBy(xpath = "//a[contains(text(),'Use Custom Domain')]")
    private WebElement useCustomDomainLink;

    @FindBy(xpath = "//h1[contains(text(),'Salesforce')]")
    private WebElement loginHeader;

    public LoginPage(WebDriver driver) {
        this.driver = driver;
        this.config = ConfigReader.getInstance();
        this.wait = new WaitUtils(driver, config.getIntProperty("explicit.wait"));
        PageFactory.initElements(driver, this);
    }

    public void enterUsername(String username) {
        try {
            wait.waitForElementVisible(usernameField);
            usernameField.clear();
            usernameField.sendKeys(username);
        } catch (Exception e) {
            throw new RuntimeException("Failed to enter username: " + e.getMessage(), e);
        }
    }

    public void enterPassword(String password) {
        try {
            wait.waitForElementVisible(passwordField);
            passwordField.clear();
            passwordField.sendKeys(password);
        } catch (Exception e) {
            throw new RuntimeException("Failed to enter password: " + e.getMessage(), e);
        }
    }

    public void clickLogin() {
        try {
            wait.waitForElementClickable(loginButton);
            loginButton.click();
        } catch (Exception e) {
            throw new RuntimeException("Failed to click login button: " + e.getMessage(), e);
        }
    }

    public void doLogin(String username, String password) {
        enterUsername(username);
        enterPassword(password);
        clickLogin();
    }

    public void doLoginWithValidCredentials() {
        String user = config.getProperty("valid.username");
        String pass = config.getProperty("valid.password");
        doLogin(user, pass);
    }

    public String getErrorMessageText() {
        try {
            wait.waitForElementVisible(errorMessage);
            return errorMessage.getText();
        } catch (Exception e) {
            throw new RuntimeException("Failed to retrieve error message: " + e.getMessage(), e);
        }
    }

    public boolean isErrorMessageDisplayed() {
        try {
            wait.waitForElementVisible(errorMessage);
            return errorMessage.isDisplayed();
        } catch (Exception e) {
            return false;
        }
    }

    public void checkRememberMe() {
        try {
            if (!rememberMeCheckbox.isSelected()) {
                rememberMeCheckbox.click();
            }
        } catch (Exception e) {
            throw new RuntimeException("Failed to check Remember Me: " + e.getMessage(), e);
        }
    }

    public void uncheckRememberMe() {
        try {
            if (rememberMeCheckbox.isSelected()) {
                rememberMeCheckbox.click();
            }
        } catch (Exception e) {
            throw new RuntimeException("Failed to uncheck Remember Me: " + e.getMessage(), e);
        }
    }

    public boolean isRememberMeChecked() {
        try {
            return rememberMeCheckbox.isSelected();
        } catch (Exception e) {
            throw new RuntimeException("Failed to check Remember Me state: " + e.getMessage(), e);
        }
    }

    public boolean isUsernameFieldDisplayed() {
        try {
            return usernameField.isDisplayed();
        } catch (Exception e) {
            return false;
        }
    }

    public boolean isPasswordFieldDisplayed() {
        try {
            return passwordField.isDisplayed();
        } catch (Exception e) {
            return false;
        }
    }

    public boolean isLoginButtonDisplayed() {
        try {
            return loginButton.isDisplayed();
        } catch (Exception e) {
            return false;
        }
    }

    public boolean isForgotPasswordLinkDisplayed() {
        try {
            return forgotPasswordLink.isDisplayed();
        } catch (Exception e) {
            return false;
        }
    }

    public boolean isLoginHeaderDisplayed() {
        try {
            return loginHeader.isDisplayed();
        } catch (Exception e) {
            return false;
        }
    }

    public String getPageTitle() {
        try {
            return driver.getTitle();
        } catch (Exception e) {
            throw new RuntimeException("Failed to get page title: " + e.getMessage(), e);
        }
    }

    public String getCurrentUrl() {
        try {
            return driver.getCurrentUrl();
        } catch (Exception e) {
            throw new RuntimeException("Failed to get current URL: " + e.getMessage(), e);
        }
    }

    public void waitForPageToLoad() {
        try {
            wait.waitForElementVisible(loginButton);
        } catch (Exception e) {
            throw new RuntimeException("Page did not load within timeout: " + e.getMessage(), e);
        }
    }
}
