$(".single-item").slick({
  dots: true
});

$('.multiple-items').slick({
  infinite: true,
  slidesToShow: 3,
  slidesToScroll: 3
});

function authorInfo(id, fullName) {
  console.log(id)
  document.getElementById('id').value=id;
  document.getElementById('authorName').value=fullName;
};

function goBack() {
    window.history.back();
}

function onSignIn(googleUser) {
  var profile = googleUser.getBasicProfile();
  console.log('ID: ' + profile.getId()); // Do not send to your backend! Use an ID token instead.
  console.log('Name: ' + profile.getName());
  console.log('Image URL: ' + profile.getImageUrl());
  console.log('Email: ' + profile.getEmail()); // This is null if the 'email' scope is not present.
};
