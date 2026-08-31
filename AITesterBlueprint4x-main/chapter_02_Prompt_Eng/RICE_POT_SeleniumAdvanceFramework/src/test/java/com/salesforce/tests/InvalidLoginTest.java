package com.salesforce.tests;

import org.testng.Assert;
import org.testng.annotations.Test;

import com.salesforce.base.BaseTest;

public class InvalidLoginTest extends BaseTest {

    @Test(priority = 1, description = "Verify error message on login with invalid password")
    public void loginWithInvalidPassword() {
        try {
            loginPage.waitForPageToLoad();
            String validUser = config.getProperty("valid.username");
            String invalidPass = config.getProperty("invalid.password");
            loginPage.doLogin(validUser, invalidPass);
            Assert.assertTrue(loginPage.isErrorMessageDisplayed(), "Error message not displayed for invalid password");
            Assert.assertTrue(
                loginPage.getCurrentUrl().contains("login"),
                "URL should still contain 'login' after failed attempt"
            );
        } catch (Exception e) {
            Assert.fail("Invalid password test failed: " + e.getMessage(), e);
        }
    }

    @Test(priority = 2, description = "Verify error on login with empty username")
    public void loginWithEmptyUsername() {
        try {
            loginPage.waitForPageToLoad();
            loginPage.doLogin("", config.getProperty("invalid.password"));
            Assert.assertTrue(loginPage.isErrorMessageDisplayed(), "Error message not displayed for empty username");
            Assert.assertTrue(
                loginPage.getCurrentUrl().contains("login"),
                "URL should still contain 'login' after empty username attempt"
            );
        } catch (Exception e) {
            Assert.fail("Empty username test failed: " + e.getMessage(), e);
        }
    }

    @Test(priority = 3, description = "Verify error on login with empty password")
    public void loginWithEmptyPassword() {
        try {
            loginPage.waitForPageToLoad();
            loginPage.doLogin(config.getProperty("valid.username"), "");
            Assert.assertTrue(loginPage.isErrorMessageDisplayed(), "Error message not displayed for empty password");
            Assert.assertTrue(
                loginPage.getCurrentUrl().contains("login"),
                "URL should still contain 'login' after empty password attempt"
            );
        } catch (Exception e) {
            Assert.fail("Empty password test failed: " + e.getMessage(), e);
        }
    }

    @Test(priority = 4, description = "Verify error on login with both fields empty")
    public void loginWithBothFieldsEmpty() {
        try {
            loginPage.waitForPageToLoad();
            loginPage.doLogin("", "");
            Assert.assertTrue(loginPage.isErrorMessageDisplayed(), "Error message not displayed for empty fields");
            Assert.assertTrue(
                loginPage.getCurrentUrl().contains("login"),
                "URL should still contain 'login' after both-empty attempt"
            );
        } catch (Exception e) {
            Assert.fail("Both fields empty test failed: " + e.getMessage(), e);
        }
    }

    @Test(priority = 5, description = "Verify error on login with invalid email format")
    public void loginWithInvalidEmailFormat() {
        try {
            loginPage.waitForPageToLoad();
            loginPage.doLogin("not-an-email", config.getProperty("invalid.password"));
            Assert.assertTrue(loginPage.isErrorMessageDisplayed(), "Error message not displayed for invalid email format");
            Assert.assertTrue(
                loginPage.getCurrentUrl().contains("login"),
                "URL should still contain 'login' after invalid email attempt"
            );
        } catch (Exception e) {
            Assert.fail("Invalid email format test failed: " + e.getMessage(), e);
        }
    }
}
