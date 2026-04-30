# Project Idea

Replace the URLs in this part.

```js
// --------- (3) Replace ORIGINAL_URL with a new image link------------------//
var ORIGINAL_URL = "https://codehs.com/uploads/295db4a40e64b25920041421ed89ace8"
// --------- (3) Replace SECRET_URL with a new image link-------------------//
var SECRET_URL = "https://codehs.com/uploads/8142469eb92d8e85455450a8dd402200"
```

Replace the `encrypt()` function with this.

```js
// (1) This function will encrypt the message in the encrypted image by
// updating the red channel for the pixel only.
// See project guide for requirements.
// no parameters or return; uses global variables
function encrypt() {
  // Step 1: Make all red channels in encrypted image even
  for (var x = 0; x < IMAGE_WIDTH; x++) {
    for (var y = 0; y < IMAGE_HEIGHT; y++) {
      encrypted.setRed(x, y, image.getRed(x, y))
      encrypted.setGreen(x, y, image.getGreen(x, y))
      encrypted.setBlue(x, y, image.getBlue(x, y))

      if (encrypted.getRed(x, y) % 2 != 0) {
        encrypted.setRed(x, y, encrypted.getRed(x, y) - 1)
      }
    }
  }

  // Step 2: For black pixels in secret image, set red channel to odd
  for (var x = 0; x < IMAGE_WIDTH; x++) {
    for (var y = 0; y < IMAGE_HEIGHT; y++) {
      if (
        secretMessage.getRed(x, y) < 128 &&
        secretMessage.getGreen(x, y) < 128 &&
        secretMessage.getBlue(x, y) < 128
      ) {
        encrypted.setRed(x, y, encrypted.getRed(x, y) + 1)
      }
    }
  }
}
```

Replace the `decrypt()` function with this.

```js
// (2) This function will decrypt the information from the encrypted image into the
// decrypted image by writing either a black pixel or a white pixel.
// See project guide for requirements
// no parameters or return; uses global variables
function decrypt() {
  for (var x = 0; x < IMAGE_WIDTH; x++) {
    for (var y = 0; y < IMAGE_HEIGHT; y++) {
      if (encrypted.getRed(x, y) % 2 != 0) {
        decrypted.setRed(x, y, 0)
        decrypted.setGreen(x, y, 0)
        decrypted.setBlue(x, y, 0)
      } else {
        decrypted.setRed(x, y, 255)
        decrypted.setGreen(x, y, 255)
        decrypted.setBlue(x, y, 255)
      }
    }
  }
}
```
