var vm = new Vue({
  el: 'main',
  data: {
    back: '',
    picture: 'https://image.flaticon.com/icons/svg/149/149992.svg',
    name: '',
    birth: '',
    email: '',
    phone: '',
    nationality: '',
  },
  beforeMount() {
    this.generate();
  },
  methods: {
    generate (gender) {
      var self = this;

      $.ajax({
        url: 'https://uinames.com/api/?ext&maxlen=15' + ((gender != null && (gender == "male" || gender == "female")) ? '&gender=' + gender : ''),
        dataType: 'json',
        success: function(data) {

          self.name = data.title + ' ' + data.name + ' ' + data.surname;

          self.gender = data.gender;

          self.birth = new Date(data.birthday.raw*1000).toLocaleDateString("en-US", { year: 'numeric', month: 'long', day: 'numeric' }) + ' (' + data.age + ' years old)';

          self.email = data.email;

          self.phone = data.phone;

          self.nationality = data.region;

          self.picture = data.photo;


          var color = getRandomColor();
          var color1 = shadeColor(color, 40);
          var color2 = shadeColor(color, -40);
          self.back = "linear-gradient(45deg, " + color1 + " 0%, " + color2 + " 100%)";
        }
      });
    },
  }
});

// generate a random color for design
function getRandomColor() {
  var brightness = 4;

  var rgb = [Math.random() * 256, Math.random() * 256, Math.random() * 256];
  var mix = [brightness*51, brightness*51, brightness*51]; //51 => 255/5
  var mixedrgb = [rgb[0] + mix[0], rgb[1] + mix[1], rgb[2] + mix[2]].map(function(x){ return Math.round(x/2.0)})
  return rgbToHex(mixedrgb[0], mixedrgb[1], mixedrgb[2]);
}

// Shade an hex color
function shadeColor(color, percent) {
  var R = parseInt(color.substring(1, 3), 16);
  var G = parseInt(color.substring(3, 5), 16);
  var B = parseInt(color.substring(5, 7), 16);
  R = parseInt(R * (100 + percent) / 100);
  G = parseInt(G * (100 + percent) / 100);
  B = parseInt(B * (100 + percent) / 100);
  R = (R < 255) ? R : 255;
  G = (G < 255) ? G : 255;
  B = (B < 255) ? B : 255;
  var RR = ((R.toString(16).length == 1) ? "0" + R.toString(16) : R.toString(16));
  var GG = ((G.toString(16).length == 1) ? "0" + G.toString(16) : G.toString(16));
  var BB = ((B.toString(16).length == 1) ? "0" + B.toString(16) : B.toString(16));
  return "#" + RR + GG + BB;
}

function rgbToHex(red, green, blue) {
  var rgb = blue | (green << 8) | (red << 16);
  return '#' + (0x1000000 + rgb).toString(16).slice(1)
}