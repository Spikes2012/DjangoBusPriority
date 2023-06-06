function displayMessage() {
  document.getElementById("progress-bar-message").style.display = "block";
  setInterval(updateDisplayMessage, 1000);
}


function updateDisplayMessage() {
  var msg = document.getElementById("progress-bar-message").innerHTML;

  if (msg == "Starting Progress...") {
    document.getElementById("progress-bar-message").innerHTML = "Checking File..";
  }

  if (msg == "Checking File..") {
    document.getElementById("progress-bar-message").innerHTML = "Checking File....";
  }

  if (msg == "Checking File....") {
    document.getElementById("progress-bar-message").innerHTML = "Checking File......";
  }

  if (msg == "Checking File......") {
    document.getElementById("progress-bar-message").innerHTML = "Checking File..";
  }
}