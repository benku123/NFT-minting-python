const inputs = document.querySelectorAll('.input');

function addcl() {
  let parent = this.parentNode.parentNode;
  parent.classList.add('focus');
}

function remcl() {
  let parent = this.parentNode.parentNode;
  if (this.value == '') {
    parent.classList.remove('focus');
  }
}

inputs.forEach(input => {
  input.addEventListener('focus', addcl);
  input.addEventListener('blur', remcl);
});

if (typeof window.ethereum !== 'undefined') {
  console.log('MetaMask is installed!');
}

// async function connectMetaMask() {
//     if (typeof window.ethereum !== 'undefined') {
//         try {
//             const accounts = await ethereum.request({ method: 'eth_requestAccounts' });
//             const account = accounts[0];
//             console.log('Connected account:', account);
//             sendAccountToServer(account);
//         } catch (error) {
//             console.error('Error connecting to MetaMask:', error);
//         }
//     } else {
//         alert('MetaMask is not installed!');
//     }
// }

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + '=') {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

function openModal(imageId) {
  var modal = document.getElementById('myModal-' + imageId);
  var img = document.getElementById('myImg-' + imageId);
  var modalImg = document.getElementById('img01-' + imageId);
  modal.style.display = 'block';
  modalImg.src = img.src;
  document.querySelector('.row').classList.add('blurred');
}

var modals = document.querySelectorAll('.modal');
modals.forEach(modal => {
  var span = modal.querySelector('.close');
  if (span) {
    span.onclick = function () {
      modal.style.display = 'none';
      document.querySelector('.row').classList.remove('blurred');
    };
  }
});

window.onclick = function (event) {
  modals.forEach(modal => {
    if (event.target == modal) {
      modal.style.display = 'none';
      document.querySelector('.row').classList.remove('blurred');
    }
  });
};

document.addEventListener('DOMContentLoaded', function () {
  var modals = document.querySelectorAll('.modal');
  var images = document.querySelectorAll('.modal-content');

  images.forEach(function (image) {
    image.addEventListener('click', function (event) {
      var modal = document.getElementById('myModal-' + image.id.split('-')[1]);
      modal.style.display = 'block';
      document.body.style.filter = 'blur(5px)';
    });
  });

  modals.forEach(function (modal) {
    modal.addEventListener('click', function (event) {
      if (event.target === modal) {
        modal.style.display = 'none';
        document.body.style.filter = 'none';
      }
    });
  });
});


