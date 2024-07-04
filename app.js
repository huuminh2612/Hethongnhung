document.addEventListener("DOMContentLoaded", function () {
  // Kết nối MQTT
  var client = mqtt.connect("wss://broker.hivemq.com:8884/mqtt");

  // Lấy các vị trí cần điền dữ liệu
  var temp = document.getElementById("ESP32_01_Temp");
  var gas = document.getElementById("ESP32_01_Gas");
  var humidity = document.getElementById("ESP32_01_Humd");

  // Kiểm tra xem các vị trí đã tìm thấy trong DOM chưa
  if (temp && gas && humidity) {
    // Subcribe vào các topic
    client.on("connect", function () {
      console.log("Connected to shiftr.io broker");
      client.subscribe("temperature");
      client.subscribe("gas");
      client.subscribe("humidity");
    });

    // Lấy tin nhắn từ các topic và cập nhật dữ liệu tương ứng
    client.on("message", function (topic, message) {
      if (topic === "temperature") {
        temp.innerHTML = message.toString();
      } else if (topic === "gas") {
        gas.innerHTML = message.toString();
      } else if (topic === "humidity") {
        humidity.innerHTML = message.toString();
      }
    });
  } else {
    console.error("One or more elements not found in the DOM.");
  }
});