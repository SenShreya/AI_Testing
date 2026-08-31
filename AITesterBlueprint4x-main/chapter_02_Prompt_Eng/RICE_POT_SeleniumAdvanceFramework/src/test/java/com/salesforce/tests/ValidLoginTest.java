package com.salesforce.tests;

import org.testng.Assert;
import org.testng.annotations.Test;

import com.salesforce.base.BaseTest;

public class ValidLoginTest extends BaseTest {

    @Test(priority = 1, description = "Verify login with valid credentials navigates away from login page")
    public void loginWithValidCredentials() {
        try {
            loginPage.waitForPageToLoad();
            Assert.assertTrue(loginPage.isUsernameFieldDisplayed(), "Username field not displayed");
            Assert.assertTrue(loginPage.isPasswordFieldDisplayed(), "Password field not displayed");
            Assert.assertTrue(loginPage.isLoginButtonDisplayed(), "Login button not displayed");
            loginPage.doLoginWithValidCredentials();
            Assert.assertTrue(
                loginPage.getCurrentUrl().contains("lightning") || !loginPage.getCurrentUrl().contains("login"),
                "Login failed: still on login page. URL: " + loginPage.getCurrentUrl()
            );
        } catch (Exception e) {
            Assert.fail("Valid login test failed: " + e.getMessage(), e);
        }
    }

    @Test(priority = 2, description = "Verify login with Remember Me checked")
    public void loginWithRememberMeChecked() {
        try {
            loginPage.waitForPageToLoad();
            loginPage.checkRememberMe();
            Assert.assertTrue(loginPage.isRememberMeChecked(), "Remember Me checkbox not checked");
            loginPage.doLoginWithValidCredentials();
            Assert.assertTrue(
                loginPage.getCurrentUrl().contains("lightning") || !loginPage.getCurrentUrl().contains("login"),
                "Login with Remember Me failed. URL: " + loginPage.getCurrentUrl()
            );
        } catch (Exception e) {
            Assert.fail("Remember Me login test failed: " + e.getMessage(), e);
        }
    }

    @Test(priority = 3, description = "Verify all UI elements are rendered on login page")
    public void verifyLoginPageUIElements() {
        try {
            loginPage.waitForPageToLoad();
            Assert.assertTrue(loginPage.isLoginHeaderDisplayed(), "Login header not displayed");
            Assert.assertTrue(loginPage.isUsernameFieldDisplayed(), "Username field not displayed");
            Assert.assertTrue(loginPage.isPasswordFieldDisplayed(), "Password field not displayed");
            Assert.assertTrue(loginPage.isLoginButtonDisplayed(), "Login button not displayed");
            Assert.assertTrue(loginPage.isForgotPasswordLinkDisplayed(), "Forgot Password link not displayed");
            Assert.assertEquals(loginPage.getPageTitle(), "Login | Salesforce", "Page title mismatch");
        } catch (Exception e) {
            Assert.fail("UI verification test failed: " + e.getMessage(), e);
        }
    }
}
