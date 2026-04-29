//--------------------- GLOBAL VARIABLES ------------------------//
var a
var b
var p
var g
var sharedPrivateKey

var possiblePs = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
var possibleGs = [
  [2],
  [2, 3],
  [3, 5],
  [2, 6, 7, 8],
  [2, 6, 7, 11],
  [3, 5, 6, 7, 10, 11, 12, 14],
  [2, 3, 10, 13, 14, 15],
  [5, 7, 10, 11, 14, 15, 17, 19, 20, 21],
  [2, 3, 8, 10, 11, 14, 15, 18, 19, 21, 26, 27],
  [3, 11, 12, 13, 17, 21, 22, 24]
]

generatePandG()

//--------------------- ONEVENTS ------------------------//

// When the user clicks the button to generate the shared key
// the DH function is called using the global variables
onEvent("generateSharedKeyBtn", "click", function () {
  a = getNumber("aSecretNum")
  b = getNumber("bSecretNum")
  sharedPrivateKey = DH(a, b)
  setText("secretKeyOutput", sharedPrivateKey)
})

// User must enter a NUMBER in the "numToEncrypt" input box
onEvent("encryptBtn", "click", function () {
  var num = getNumber("numToEncrypt")
  var result = encryptDH(num)
  setText("encryptedNum", result)
})

// User must enter a NUMBER in the "numToDecrypt" input box
onEvent("decryptBtn", "click", function () {
  var num = getNumber("numToDecrypt")
  var result = decryptDH(num)
  while (result < 0) {
    result += p
  }
  setText("decryptedNum", result)
})

// clicking the next button changes the screen
onEvent("nextButton", "click", function () {
  setScreen("screen2")
})

// clicking the home button changes the app to screen1 and resests all screen elements
onEvent("homeButton", "click", function () {
  setScreen("screen1")
  clearAndReset()
})

// clicking the refresh button resests all screen elements
onEvent("refreshButton", "click", function () {
  clearAndReset()
})

//--------------------- FUNCTIONS ------------------------//

// This function will compute and return the Shared Key from Alice & Bob
// a {number} - the secret value that Alice chooses
// b {number} - the secret value that Bob chooses
// return {number} - the generated shared key once verified that Alice & Bob
//                    BOTH generated the same shared key
function DH(a, b) {
  // your code here
}

// This function encrypts a number t and returns the encrypted value
// t {number} - the value to encrypt
// return {number} - the encrypted value
function encryptDH(t) {
  //your code here
}

// This function decrypts a number c and returns the decrypted value
// c {number} - the value to edecrypt
// return {number} - the decrypted value
function decryptDH(c) {
  //your code here
}

// done for you
function generatePandG() {
  // randomly choose p from possiblePs
  var randP = Math.floor(Math.random() * 10)
  p = possiblePs[randP]

  //randomly choose g from possibleGs now that we have chosen p
  var size = possibleGs[randP].length
  var randG = Math.floor(Math.random() * size)
  g = possibleGs[randP][randG]

  updateScreenPG()
}

function updateScreenPG() {
  setText("pValue", "p: " + p)
  setText("gValue", "g: " + g)
}

// clears and resets all screen elements
function clearAndReset() {
  setText("aSecretNum", "")
  setText("bSecretNum", "")
  setText("secretKeyOutput", "")
  setText("numToEncrypt", "")
  setText("encryptedNum", "")
  setText("numToDecrypt", "")
  setText("decryptedNum", "")
  setText("pValue", "p: ")
  setText("gValue", "g: ")
  generatePandG()
}
