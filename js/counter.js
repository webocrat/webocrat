  var updateSpeed = 100;
   
  function updateCounter() {
     counterValue += counterSpeed/60/1000*updateSpeed;
     tc = String(Math.round(counterValue));
     while(tc.length<9) { tc = "x" + tc; }
     for (i=1;i<9;i++) {  $("#d"+i).attr('class', "n" + tc.charAt(i)); }
  }
  
  setInterval("updateCounter()", updateSpeed);
