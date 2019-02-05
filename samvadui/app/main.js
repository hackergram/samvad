define(function (require) {
    // Load any app-specific modules
    // with a relative require call,
    // like:
    var messages = require('./messages');

    // Load library/vendor modules using
    // full IDs, like:
    var print = require('print');
    var jquery = require('jquery')
    var moment = require("moment-with-locales")
    var fetch = function(){
      jquery.getJSON("http://192.168.56.101:5000/vyakti", function(data){
          jquery("#viz").empty()
          for(i=0;i<data.resp.length;i++){
            ts=moment(data.resp[i].lastseen_timestamp.$date).format("YYYY-MM-DD HH:mm:ss")
            ts2=moment(data.resp[i].lastseen_timestamp.$date).fromNow()
            //ts=new Date(data.resp[i].lastseen_timestamp.$date)
              jquery("#viz").append("Name: "+data.resp[i].vyakti_id+" Last Seen: "+ts+", "+ts2+"<br>");
          }

      })
    }
    setInterval(fetch, 5000);// call fetch every 5 seconds
 fetch(); // call fetch first time

});
