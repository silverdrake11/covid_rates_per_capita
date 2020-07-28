 //function localizeDate() {
    var dateUTC = document.getElementsByTagName('body')[0];
    var dateObj = new Date(dateUTC.getAttribute('data-utc'));
    var options = {weekday: 'short', month: 'long', day: 'numeric', hour: 'numeric', 
        minute: 'numeric', timeZoneName: 'short'};
    var formatted = dateObj.toLocaleDateString(undefined, options);
    formatted = formatted.replace(',','');
    formatted = formatted.replace(',','&nbsp;');
    var res = formatted.split(" ");
    if (res.length == 6 && res[3].indexOf(':') > -1) {
      document.getElementsByTagName('my-date')[0].innerHTML = formatted;
    }
//}