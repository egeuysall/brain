//--------------------- GLOBAL VARIABLES ------------------------//

var primes = generatePrimes()
var p = 0
var q = 0
var n
var m
var e
var d

//--------------------- ONEVENTS ------------------------//

// screen2 randomly generates p & q
onEvent("goScreen2Button", "click", function () {
  setScreen("screen2")
  pickTwoPrimes()
  setText("pLabel", "p = " + p)
  setText("qLabel", "q = " + q)
})

// screen3 allows user to input p & q values
onEvent("goScreen3Button", "click", function () {
  setScreen("screen3")
  clearAndReset()
  p = 0
  q = 0
})

// screen2 randomly generates p & q
onEvent("goScreen2Button2", "click", function () {
  setScreen("screen2")
  pickTwoPrimes()
  setText("pLabel", "p = " + p)
  setText("qLabel", "q = " + q)
})

// screen3 allows user to input p & q values
onEvent("goScreen3Button2", "click", function () {
  setScreen("screen3")
})

// Uses global variables to generate public and private keys
onEvent("generateKeysBtn", "click", function () {
  RSA()
  setText("pubKeyOutput", "(" + n + ", " + e + ")")
  setText("privKeyOutput", "(" + n + ", " + d + ")")
})

// Uses global variables to generate public and private keys
onEvent("generateKeysBtn2", "click", function () {
  p = getNumber("pInput")
  q = getNumber("qInput")
  RSA()
  setText("pubKeyOutput2", "(" + n + ", " + e + ")")
  setText("privKeyOutput2", "(" + n + ", " + d + ")")
})

onEvent("homeButton", "click", function () {
  setScreen("screen1")
  clearAndReset()
})

onEvent("homeButton2", "click", function () {
  setScreen("screen1")
  clearAndReset()
})

onEvent("refreshButton", "click", clearAndReset)
onEvent("refreshButton2", "click", clearAndReset)

//--------------------- FUNCTIONS ------------------------//

// This function will compute Alice's Public and Private Key using global variables
// no return, update global variables
function RSA() {
  //your code here
  // find e such that 1 < e < n and e must be coprime to m
  // find d such that (e * d) % m == 1
}

// done for you
// no parameters, uses global variables
// return {array} - a list of the primes numbers up to 250
function generatePrimes() {
  var primeNums = []
  for (var i = 2; i < 250; i++) {
    var sqrt = Math.floor(Math.sqrt(i))
    var isPrime = true
    for (var j = 2; j <= sqrt; j++) {
      if (i % j == 0) {
        isPrime = false
      }
    }
    if (isPrime) {
      primeNums.push(i)
    }
  }
  return primeNums
}

// done for you
// This function ensures that p and q are different primes
// no parameters, no return
function pickTwoPrimes() {
  p = primes[Math.floor(Math.random() * primes.length)]
  q = primes[Math.floor(Math.random() * primes.length)]
  while (p == q) {
    p = primes[Math.floor(Math.random() * primes.length)]
    q = primes[Math.floor(Math.random() * primes.length)]
  }
}

// Done for you
// This function returns the greatest common divisior of a and b
// a, b {number} - the numbers you are trying to find the gcd of. Assume a >= b.
// return {number} - the gcd of ints a and b
function gcd(a, b) {
  if (b == 0) {
    return a
  }
  return gcd(b, a % b)
}

// clears and resets all screen elements
// no parameters, no return
function clearAndReset() {
  pickTwoPrimes()
  n = ""
  m = ""
  d = ""
  e = ""
  setText("pLabel", "p = " + p)
  setText("qLabel", "q = " + q)
  setText("pInput", " ")
  setText("qInput", " ")
  setText("pubKeyOutput", "(n, e)")
  setText("privKeyOutput", "(n, d)")
  setText("pubKeyOutput2", "(n, e)")
  setText("privKeyOutput2", "(n, d)")
}
