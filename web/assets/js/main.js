(function ($) {
  $(window).scroll(function () {
    if ($(this).scrollTop() > 100) {
      $('.scrollup').fadeIn()
      $('.navbar').addClass('navsmall')
    } else {
      $('.scrollup').fadeOut()
      $('.navbar').removeClass('navsmall')
    }
  })

  $('.scrollup').click(function () {
    $('html, body').animate({ scrollTop: 0 }, 1000)
    return false
  })

  $('.downloadLink').on('click', function (event) {
    if (this.hash !== '') {
      event.preventDefault()

      var hash = this.hash

      $('html, body').animate({
        scrollTop: $(hash).offset().top
      }, 800, function () {
        window.location.hash = hash
      })
    }
  })
})(jQuery)

