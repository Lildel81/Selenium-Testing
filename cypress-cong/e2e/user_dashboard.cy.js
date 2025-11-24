// cypress/e2e/user_dashboard.cy.js

describe("Section 10 – User Dashboard (Cong)", () => {
  const LOGIN_EMAIL = "test@user.com";
  const LOGIN_PASSWORD = "Password123!";

  //
  // ⭐ STEP 0 – Ensure test@user.com exists before ANY tests run
  //
  before(() => {
    cy.visit("/user-signup");

    cy.get("#fullname").clear().type("Test User");
    cy.get("#email").clear().type(LOGIN_EMAIL);
    cy.get("#password").clear().type(LOGIN_PASSWORD);

    cy.get("button.signup_button").click({ force: true });

    // Signup either creates the user OR shows "email already exists"
    cy.url().then((url) => {
      if (url.includes("/user-dashboard")) {
        cy.log("User created successfully");
      } else {
        cy.get("#msg .error").should("exist");
        cy.log("User already exists, continuing tests");
      }
    });
  });

  //
  // Helper: log in as test@user.com
  //
  const loginAsTestUser = () => {
    cy.visit("/user-login");
    cy.get("#email").type(LOGIN_EMAIL);
    cy.get("#password").type(LOGIN_PASSWORD);
    cy.get("button.login_button").click({ force: true });
    cy.url().should("include", "/user-dashboard");
  };

  //
  // 10.1 Logging In
  //
  describe("10.1 Logging In", () => {
    it("10.1.2 Valid login redirects to dashboard", () => {
      cy.visit("/user-login");

      cy.get("#email").type(LOGIN_EMAIL);
      cy.get("#password").type(LOGIN_PASSWORD);
      cy.get("button.login_button").click({ force: true });

      cy.url().should("include", "/user-dashboard");
      cy.contains("My Dashboard").should("exist");
      cy.contains("Welcome back").should("exist");
    });

    it("10.1.3 Invalid login shows error message", () => {
      cy.visit("/user-login");

      cy.get("#email").type(LOGIN_EMAIL);
      cy.get("#password").type("WrongPass123!");
      cy.get("button.login_button").click({ force: true });

      cy.get("#msg .error").should("exist");
      cy.url().should("include", "/user-login");
    });
  });

  //
  // 10.2 Signing Up
  //
  describe("10.2 Signing Up", () => {
    it("10.2.2 Valid signup with test@user.com (first time logs in, later runs show 'already exists')", () => {
      cy.visit("/user-signup");

      cy.get("#fullname").type("Test User");
      cy.get("#email").type(LOGIN_EMAIL);
      cy.get("#password").type(LOGIN_PASSWORD);
      cy.get("button.signup_button").click({ force: true });

      cy.url().then((url) => {
        if (url.includes("/user-dashboard")) {
          cy.contains("My Dashboard").should("exist");
        } else {
          cy.get("#msg .error").should("exist");
        }
      });
    });

    it("10.2.3 Invalid signup (missing fields) shows error message", () => {
      cy.visit("/user-signup");

      cy.get("#email").type("invalid@example.com");
      cy.get("button.signup_button").click({ force: true });

      cy.get("#msg .error").should("exist");
    });
  });

  //
  // 10.3 Update Email (UI check only)
  //
  describe("10.3 Update Email (UI Check)", () => {
    beforeEach(() => {
      loginAsTestUser();
    });

    it("10.3.2 Update Email form shows correct current email", () => {
      cy.get("#currentEmail").should("exist").and("have.value", LOGIN_EMAIL);

      cy.get("#newEmail").should("exist");
      cy.get("#confirmPassword").should("exist");
      cy.get("#update-email-form button[type='submit']").should("exist");
    });
  });

  //
  // 10.4 Change Password (UI check only)
  //
  describe("10.4 Change Password (UI Check)", () => {
    beforeEach(() => {
      loginAsTestUser();
    });

    it("10.4.2 Change Password form fields are visible", () => {
      cy.get("#currentPassword").should("exist");
      cy.get("#newPassword").should("exist");
      cy.get("#confirmNewPassword").should("exist");
      cy.get("#change-password-form button[type='submit']").should("exist");
      cy.contains("Minimum 8 characters").should("exist");
    });
  });

  //
  // 10.5 Navigate to Energy Leak Quiz
  //
  describe("10.5 Navigate to Energy Leak Quiz", () => {
    beforeEach(() => {
      loginAsTestUser();
    });

    it("10.5.2 Button redirects to Energy Leak intro page", () => {
      cy.contains("a", "Take Your First Assessment").click({ force: true });
      cy.url().should("include", "/intro");
      cy.contains("Energy Leak").should("exist");
    });
  });

  //
  // 10.6 Book Appointment Navigation
  //
  describe("10.6 Book Appointment", () => {
    beforeEach(() => {
      loginAsTestUser();
    });

    it("10.6.2 Button redirects to booking page", () => {
      cy.contains("a", "Book Now").click({ force: true });
      cy.url().should("include", "/booking");
      cy.contains("Select a Date").should("exist");
    });
  });

  //
  // 10.7 Delete Account Modal
  //
  describe("10.7 Delete Account", () => {
    beforeEach(() => {
      // Make sure the test user exists and is logged in
      loginAsTestUser();
    });

    it("10.7.2 Enter password and delete account, then login is no longer possible", () => {
      // Open the delete modal
      cy.get("#open-delete-modal").click({ force: true });

      // Modal should be visible with password field
      cy.get("#deleteModal").should("exist");
      cy.get("#deletePassword").should("exist");

      // Automatically enter the password and confirm deletion
      cy.get("#deletePassword").type(LOGIN_PASSWORD);
      cy.contains("button", "Yes, Delete My Account").click({ force: true });

      // After deletion, you should no longer be on the dashboard
      cy.url().should("not.include", "/user-dashboard");

      // Try to log in again with the same credentials
      cy.visit("/user-login");
      cy.get("#email").type(LOGIN_EMAIL);
      cy.get("#password").type(LOGIN_PASSWORD);
      cy.get("button.login_button").click({ force: true });

      // Expect an error because the account was deleted
      cy.get("#msg .error").should("exist");
      cy.url().should("include", "/user-login");
    });
  });
});
