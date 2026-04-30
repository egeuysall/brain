/*
 * This program will show how we can use steganography
 * to encrypt a secret message inside of a cover image without the cover
 * image looking modified.
 *
 */

// Increase our canvas size for this exercise
setSize(465, 2100)

//GLOBAL VARIABLES----------------------------------------------------------

// Constants for the image
var GAP = 60
var LABEL_GAP = 45

// --------- (3) Replace ORIGINAL_URL with a new image link------------------//
var ORIGINAL_URL = "https://codehs.com/uploads/295db4a40e64b25920041421ed89ace8"
// --------- (3) Replace SECRET_URL with a new image link-------------------//
var SECRET_URL = "https://codehs.com/uploads/8142469eb92d8e85455450a8dd402200"

// ----------------------- DO NOT Change these links -----------------------//
var ENCRYPTED_URL =
  "https://codehs.com/uploads/681003b01c9cf08e635f1918b715921a"
var DECRYPTED_URL =
  "https://codehs.com/uploads/61feadea94bbdb34769ea08c73cdb1bc"

//----------------------Adjust width & height as needed--------------------//
var IMAGE_WIDTH = 450
var IMAGE_HEIGHT = 450

var IMAGE_X = 10
var IMAGE_Y = 50

// We need to wait for the image to load before modifying it
var IMAGE_LOAD_WAIT_TIME = 3000

// Images
var image
var secretMessage
var encrypted
var decrypted

function start() {
  addImages()
  addLabels()

  setTimeout(function () {
    encrypt()
    decrypt()
  }, IMAGE_LOAD_WAIT_TIME)
}

// (1) This function will encrypt the message in the encrypted image by
// updating the red channel for the pixel only.
// See project guide for requirements.
// no parameters or return; uses global variables
function encrypt() {
  for (var x = 0; x < IMAGE_WIDTH; x++) {
    for (var y = 0; y < IMAGE_HEIGHT; y++) {
      if (encrypted.getRed(x, y) % 2 != 0) {
        encrypted.setRed(x, y, image.getRed(x, y) + 1)
      }

      if (encrypted.getRed(x, y) == 0 && encrypted.getGreen(x)) {
      }
    }
  }

  console.log(encrypted.getRed(5, 10))

  for (var x = 0; x < IMAGE_WIDTH; x++) {
    for (var y = 0; y < IMAGE_HEIGHT; y++) {}
  }
}

// (2) This function will decrypt the information from the encrypted image into the
// decrypted image by writing either a black pixel or a white pixel.
// See project guide for requirements
// no parameters or return; uses global variables
function decrypt() {
  // Your code here
}

//-----------------DON'T MODIFY ANY CODE BELOW THIS LINE--------------------//
/*
 * This function is complete and will load all images before we process
 * them. Images need to be loaded so that we can have access
 * to the data, so we will first set up all images.
 * Each image should be sized to be IMAGE_WIDTH, IMAGE_HEIGHT.
 * When the images are loaded, you should see the labels at the
 * top of each image.
 */
function addImages() {
  // Add all 4 images here

  // the original color image
  image = new WebImage(ORIGINAL_URL)
  image.setSize(IMAGE_WIDTH, IMAGE_HEIGHT)
  image.setPosition(IMAGE_X, IMAGE_Y)

  // the secret black and white image
  secretMessage = new WebImage(SECRET_URL)
  secretMessage.setSize(IMAGE_WIDTH, IMAGE_HEIGHT)
  secretMessage.setPosition(IMAGE_X, IMAGE_Y + (GAP + IMAGE_HEIGHT))

  // the encrypted image
  encrypted = new WebImage(ENCRYPTED_URL)
  encrypted.setSize(IMAGE_WIDTH, IMAGE_HEIGHT)
  encrypted.setPosition(IMAGE_X, IMAGE_Y + 2 * (GAP + IMAGE_HEIGHT))

  // the decrypted image
  decrypted = new WebImage(DECRYPTED_URL)
  decrypted.setSize(IMAGE_WIDTH, IMAGE_HEIGHT)
  decrypted.setPosition(IMAGE_X, IMAGE_Y + 3 * (GAP + IMAGE_HEIGHT))

  // Load all the data for each image
  add(image)
  add(secretMessage)
  add(encrypted)
  add(decrypted)
}

/*
 * This function is complete and adds labels between the images.
 * You should not update this code. If your images overlap the labels
 * update your images, not this code.
 */
function addLabels() {
  // Add original label
  var originalLabel = new Text(
    "//-------------------- Original Image --------------------//",
    "14pt Arial"
  )
  originalLabel.setPosition(image.getX(), LABEL_GAP)
  add(originalLabel)

  // Add message label
  var messageLabel = new Text(
    "//-------------------- Secret Image --------------------//",
    "14pt Arial"
  )
  messageLabel.setPosition(
    image.getX(),
    image.getY() + LABEL_GAP + IMAGE_HEIGHT
  )
  add(messageLabel)

  // Add encrypted label
  var encryptedLabel = new Text(
    "//-------------------- Encrypted Image --------------------//",
    "14pt Arial"
  )
  encryptedLabel.setPosition(
    image.getX(),
    image.getY() + LABEL_GAP + GAP + 2 * IMAGE_HEIGHT
  )
  add(encryptedLabel)

  // Add decrypted label
  var decryptedLabel = new Text(
    "//-------------------- Decrypted Image --------------------//",
    "14pt Arial"
  )
  decryptedLabel.setPosition(
    image.getX(),
    image.getY() + LABEL_GAP + 2 * GAP + 3 * IMAGE_HEIGHT
  )
  add(decryptedLabel)
}
