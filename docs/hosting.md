# Hosting and Security Configuration

This document provides security configuration guidance for hosting the Exposure gallery.

## Content Security Policy (CSP)

To protect against XSS attacks and ensure data integrity, configure the following Content Security Policy headers on your web server.

### Recommended CSP Headers

```http
Content-Security-Policy: default-src 'none'; img-src 'self' data:; script-src 'self'; style-src 'self'; font-src 'self'; object-src 'none'; base-uri 'self'; form-action 'none'; frame-ancestors 'none';
```

### Header Breakdown

- `default-src 'none'`: Block all resources by default (whitelist approach)
- `img-src 'self' data:`: Allow images from same origin + data URLs (for inline SVG)
- `script-src 'self'`: Only allow JavaScript from same origin
- `style-src 'self'`: Only allow CSS from same origin
- `font-src 'self'`: Only allow fonts from same origin (if added later)
- `object-src 'none'`: Block plugins (Flash, Java, etc.)
- `base-uri 'self'`: Prevent `<base>` tag injection
- `form-action 'none'`: No forms present in gallery
- `frame-ancestors 'none'`: Prevent embedding in iframes (clickjacking protection)

### Server-Specific Configuration

#### Nginx

Add to your server block:

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    root /path/to/exposure/dist;

    # Security Headers
    add_header Content-Security-Policy "default-src 'none'; img-src 'self' data:; script-src 'self'; style-src 'self'; font-src 'self'; object-src 'none'; base-uri 'self'; form-action 'none'; frame-ancestors 'none';" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer" always;
    add_header Permissions-Policy "camera=(), microphone=(), geolocation=()" always;

    # Serve static files
    location / {
        try_files $uri $uri/ =404;
    }

    # Cache static assets
    location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

#### Apache

Add to `.htaccess` or virtual host configuration:

```apache
# Security Headers
Header always set Content-Security-Policy "default-src 'none'; img-src 'self' data:; script-src 'self'; style-src 'self'; font-src 'self'; object-src 'none'; base-uri 'self'; form-action 'none'; frame-ancestors 'none';"
Header always set X-Content-Type-Options "nosniff"
Header always set X-Frame-Options "DENY"
Header always set X-XSS-Protection "1; mode=block"
Header always set Referrer-Policy "no-referrer"
Header always set Permissions-Policy "camera=(), microphone=(), geolocation=()"

# Cache static assets
<filesMatch "\.(jpg|jpeg|png|gif|ico|css|js)$">
    Header set Cache-Control "max-age=31536000, public, immutable"
</filesMatch>
```

#### GitHub Pages

GitHub Pages automatically sets some security headers. For additional CSP, use the `_headers` file (requires GitHub Pages custom domain):

```
/*
  Content-Security-Policy: default-src 'none'; img-src 'self' data:; script-src 'self'; style-src 'self'; font-src 'self'; object-src 'none'; base-uri 'self'; form-action 'none'; frame-ancestors 'none';
  X-Content-Type-Options: nosniff
  X-Frame-Options: DENY
  Referrer-Policy: no-referrer
```

#### Netlify

Create `netlify.toml` in repository root:

```toml
[[headers]]
  for = "/*"
  [headers.values]
    Content-Security-Policy = "default-src 'none'; img-src 'self' data:; script-src 'self'; style-src 'self'; font-src 'self'; object-src 'none'; base-uri 'self'; form-action 'none'; frame-ancestors 'none';"
    X-Content-Type-Options = "nosniff"
    X-Frame-Options = "DENY"
    X-XSS-Protection = "1; mode=block"
    Referrer-Policy = "no-referrer"
    Permissions-Policy = "camera=(), microphone=(), geolocation=()"

[[headers]]
  for = "/*.jpg"
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"

[[headers]]
  for = "/*.png"
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"

[[headers]]
  for = "/*.css"
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"

[[headers]]
  for = "/*.js"
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"
```

#### Cloudflare Pages

Create `_headers` file in `dist/` directory:

```
/*
  Content-Security-Policy: default-src 'none'; img-src 'self' data:; script-src 'self'; style-src 'self'; font-src 'self'; object-src 'none'; base-uri 'self'; form-action 'none'; frame-ancestors 'none';
  X-Content-Type-Options: nosniff
  X-Frame-Options: DENY
  X-XSS-Protection: 1; mode=block
  Referrer-Policy: no-referrer
  Permissions-Policy: camera=(), microphone=(), geolocation=()

/*.jpg
  Cache-Control: public, max-age=31536000, immutable

/*.png
  Cache-Control: public, max-age=31536000, immutable

/*.css
  Cache-Control: public, max-age=31536000, immutable

/*.js
  Cache-Control: public, max-age=31536000, immutable
```

## Additional Security Headers

### X-Content-Type-Options

```http
X-Content-Type-Options: nosniff
```

Prevents MIME type sniffing, forcing browsers to respect declared content types.

### X-Frame-Options

```http
X-Frame-Options: DENY
```

Prevents the gallery from being embedded in iframes (clickjacking protection).

### Referrer-Policy

```http
Referrer-Policy: no-referrer
```

Prevents leaking referrer information when users navigate away from your gallery.

### Permissions-Policy

```http
Permissions-Policy: camera=(), microphone=(), geolocation=()
```

Disables unnecessary browser APIs that aren't used by the gallery.

## HTTPS Configuration

**Always serve over HTTPS**. Use Let's Encrypt for free SSL certificates:

```bash
# Certbot (example for Nginx)
sudo certbot --nginx -d yourdomain.com
```

### HSTS (HTTP Strict Transport Security)

Once HTTPS is confirmed working, add HSTS header:

```http
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
```

## Subresource Integrity (SRI)

The gallery uses hashed filenames for cache busting, which provides content integrity. If you want additional SRI protection, you can generate SRI hashes:

```bash
# Generate SRI hash for a file
openssl dgst -sha384 -binary dist/gallery.abc123.js | openssl base64 -A
```

Then add to HTML (modify build_html.py if needed):

```html
<script src="gallery.abc123.js"
        integrity="sha384-HASH_HERE"
        crossorigin="anonymous"></script>
```

## Testing Your Configuration

### CSP Validator

Test your CSP at: https://csp-evaluator.withgoogle.com/

### Security Headers Check

Verify headers at: https://securityheaders.com/

### Expected Score

With the recommended configuration, you should achieve an **A+ rating** on Security Headers.

## Monitoring

Consider using:

- **Report-URI** or **Sentry** for CSP violation reporting
- Add `report-uri` directive to CSP for monitoring:

```http
Content-Security-Policy: default-src 'none'; ...; report-uri https://your-endpoint.com/csp-report
```

## Troubleshooting

### Images Not Loading

- Check `img-src 'self' data:` is present in CSP
- Verify image files are served from same origin

### JavaScript Not Executing

- Ensure `script-src 'self'` is in CSP
- No inline scripts are used (all JS is in external files)

### Styles Not Applying

- Verify `style-src 'self'` in CSP
- No inline styles or `style=""` attributes used

## References

- [MDN: Content Security Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP)
- [CSP Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Content_Security_Policy_Cheat_Sheet.html)
- [Security Headers Best Practices](https://owasp.org/www-project-secure-headers/)
