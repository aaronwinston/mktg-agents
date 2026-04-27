import {
  validateEmail,
  validateUrl,
  validateTextLength,
  validatePhoneNumber,
  validatePassword,
  validateOrgName,
  validateRequired,
  validateSignInForm,
  validateSignUpForm,
} from '../src/lib/validation';

import {
  sanitizeHtml,
  sanitizeText,
  sanitizeUrl,
  sanitizeUserInput,
  sanitizeFilename,
  containsScriptContent,
} from '../src/lib/sanitizer';

describe('Validation Tests', () => {
  describe('Email Validation', () => {
    it('should validate correct email addresses', () => {
      expect(validateEmail('user@example.com').valid).toBe(true);
      expect(validateEmail('test.user+tag@domain.co.uk').valid).toBe(true);
    });

    it('should reject invalid email addresses', () => {
      expect(validateEmail('invalid.email').valid).toBe(false);
      expect(validateEmail('user@').valid).toBe(false);
      expect(validateEmail('@example.com').valid).toBe(false);
      expect(validateEmail('').valid).toBe(false);
    });
  });

  describe('URL Validation', () => {
    it('should validate correct URLs', () => {
      expect(validateUrl('http://example.com').valid).toBe(true);
      expect(validateUrl('https://example.com/path').valid).toBe(true);
      expect(validateUrl('https://example.com:8080/path?query=value').valid).toBe(true);
    });

    it('should reject invalid URLs', () => {
      expect(validateUrl('not a url').valid).toBe(false);
      expect(validateUrl('ftp://example.com').valid).toBe(false);
      expect(validateUrl('javascript:alert(1)').valid).toBe(false);
    });
  });

  describe('Text Length Validation', () => {
    it('should validate text within limit', () => {
      expect(validateTextLength('Hello World').valid).toBe(true);
      expect(validateTextLength('a'.repeat(5000)).valid).toBe(true);
    });

    it('should reject text exceeding limit', () => {
      expect(validateTextLength('a'.repeat(5001)).valid).toBe(false);
      const result = validateTextLength('a'.repeat(5001));
      expect(result.error).toContain('5000 characters');
    });
  });

  describe('Phone Number Validation', () => {
    it('should validate correct phone numbers', () => {
      expect(validatePhoneNumber('1234567890').valid).toBe(true);
      expect(validatePhoneNumber('+1 (234) 567-8900').valid).toBe(true);
      expect(validatePhoneNumber('123-456-7890').valid).toBe(true);
      expect(validatePhoneNumber('+1234567890').valid).toBe(true);
    });

    it('should reject invalid phone numbers', () => {
      expect(validatePhoneNumber('123').valid).toBe(false);
      expect(validatePhoneNumber('abc-def-ghij').valid).toBe(false);
    });
  });

  describe('Password Validation', () => {
    it('should validate strong passwords', () => {
      expect(validatePassword('StrongPass123').valid).toBe(true);
      expect(validatePassword('Secure1Pass').valid).toBe(true);
    });

    it('should reject weak passwords', () => {
      expect(validatePassword('weak').valid).toBe(false); // Too short
      expect(validatePassword('nouppercase123').valid).toBe(false); // No uppercase
      expect(validatePassword('NOLOWERCASE123').valid).toBe(false); // No lowercase
      expect(validatePassword('NoNumbers').valid).toBe(false); // No numbers
    });
  });

  describe('Organization Name Validation', () => {
    it('should validate valid organization names', () => {
      expect(validateOrgName('Acme Corp').valid).toBe(true);
      expect(validateOrgName('My Company LLC').valid).toBe(true);
    });

    it('should reject invalid organization names', () => {
      expect(validateOrgName('').valid).toBe(false);
      expect(validateOrgName('a'.repeat(256)).valid).toBe(false);
    });
  });

  describe('Required Field Validation', () => {
    it('should validate non-empty fields', () => {
      expect(validateRequired('Some text').valid).toBe(true);
    });

    it('should reject empty fields', () => {
      expect(validateRequired('').valid).toBe(false);
      expect(validateRequired('   ').valid).toBe(false);
    });
  });

  describe('SignIn Form Validation', () => {
    it('should validate correct sign in form', () => {
      const result = validateSignInForm('user@example.com', 'password123');
      expect(result.valid).toBe(true);
      expect(result.errors).toEqual({});
    });

    it('should reject invalid sign in form', () => {
      const result = validateSignInForm('invalid', '');
      expect(result.valid).toBe(false);
      expect(result.errors.email).toBeDefined();
      expect(result.errors.password).toBeDefined();
    });
  });

  describe('SignUp Form Validation', () => {
    it('should validate correct sign up form', () => {
      const result = validateSignUpForm('user@example.com', 'StrongPass123', 'My Company');
      expect(result.valid).toBe(true);
      expect(result.errors).toEqual({});
    });

    it('should reject invalid sign up form', () => {
      const result = validateSignUpForm('invalid', 'weak', '');
      expect(result.valid).toBe(false);
      expect(result.errors.email).toBeDefined();
      expect(result.errors.password).toBeDefined();
      expect(result.errors.orgName).toBeDefined();
    });
  });
});

describe('Sanitizer Tests', () => {
  describe('HTML Sanitization', () => {
    it('should preserve safe HTML', () => {
      const safe = '<p>Hello <strong>World</strong></p>';
      expect(sanitizeHtml(safe)).toContain('Hello');
      expect(sanitizeHtml(safe)).toContain('World');
    });

    it('should remove script tags', () => {
      const unsafe = '<p>Hello</p><script>alert("XSS")</script>';
      const sanitized = sanitizeHtml(unsafe);
      expect(sanitized).not.toContain('script');
      expect(sanitized).not.toContain('alert');
    });

    it('should remove event handlers', () => {
      const unsafe = '<p onclick="alert(\'XSS\')">Click me</p>';
      const sanitized = sanitizeHtml(unsafe);
      expect(sanitized).not.toContain('onclick');
    });

    it('should remove dangerous elements', () => {
      const unsafe = '<iframe src="evil.com"></iframe>';
      const sanitized = sanitizeHtml(unsafe);
      expect(sanitized).not.toContain('iframe');
    });
  });

  describe('Text Sanitization', () => {
    it('should escape HTML entities', () => {
      const result = sanitizeText('<script>alert("XSS")</script>');
      expect(result).toContain('&lt;');
      expect(result).toContain('&gt;');
      expect(result).not.toContain('<script>');
    });

    it('should handle empty strings', () => {
      expect(sanitizeText('')).toBe('');
      expect(sanitizeText(null as any)).toBe('');
    });
  });

  describe('URL Sanitization', () => {
    it('should allow safe URLs', () => {
      expect(sanitizeUrl('http://example.com')).toBe('http://example.com');
      expect(sanitizeUrl('https://example.com/path')).toBe('https://example.com/path');
      expect(sanitizeUrl('/relative/path')).toBe('/relative/path');
      expect(sanitizeUrl('#anchor')).toBe('#anchor');
    });

    it('should block dangerous protocols', () => {
      expect(sanitizeUrl('javascript:alert("XSS")')).toBe('');
      expect(sanitizeUrl('data:text/html,<script>alert("XSS")</script>')).toBe('');
      expect(sanitizeUrl('vbscript:msgbox("XSS")')).toBe('');
    });

    it('should handle empty strings', () => {
      expect(sanitizeUrl('')).toBe('');
      expect(sanitizeUrl(null as any)).toBe('');
    });
  });

  describe('User Input Sanitization', () => {
    it('should truncate to max length', () => {
      const result = sanitizeUserInput('a'.repeat(6000), 5000);
      expect(result.length).toBeLessThanOrEqual(5000);
    });

    it('should escape HTML in user input', () => {
      const result = sanitizeUserInput('<script>alert("XSS")</script>');
      expect(result).not.toContain('<script>');
    });
  });

  describe('Filename Sanitization', () => {
    it('should remove path traversal attempts', () => {
      expect(sanitizeFilename('../../../etc/passwd')).toBe('etcpasswd');
      expect(sanitizeFilename('..\\windows\\system32')).toBe('windowssystem32');
    });

    it('should remove dangerous characters', () => {
      expect(sanitizeFilename('file<name>.txt')).toBe('filename.txt');
      expect(sanitizeFilename('file|name.txt')).toBe('filename.txt');
    });

    it('should handle empty strings', () => {
      expect(sanitizeFilename('')).toBe('');
    });
  });

  describe('Script Content Detection', () => {
    it('should detect script tags', () => {
      expect(containsScriptContent('<script>alert("XSS")</script>')).toBe(true);
    });

    it('should detect event handlers', () => {
      expect(containsScriptContent('<div onclick="alert(\'XSS\')">Click</div>')).toBe(true);
    });

    it('should detect javascript protocol', () => {
      expect(containsScriptContent('<a href="javascript:alert(\'XSS\')">Link</a>')).toBe(true);
    });

    it('should pass clean content', () => {
      expect(containsScriptContent('<p>Clean content</p>')).toBe(false);
    });
  });
});
