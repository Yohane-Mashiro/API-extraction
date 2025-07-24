// 示例JavaScript文件，用于测试API提取

// fetch API 示例
fetch('/api/users')
    .then(response => response.json())
    .then(data => console.log(data));

fetch('https://jsonplaceholder.typicode.com/posts/1')
    .then(response => response.json())
    .then(json => console.log(json));

// XMLHttpRequest 示例
const xhr = new XMLHttpRequest();
xhr.open('GET', '/api/products');
xhr.send();

// jQuery AJAX 示例
$.get('/api/orders', function(data) {
    console.log(data);
});

$.post('/api/login', {username: 'user', password: 'pass'});

// axios 示例
axios.get('/api/dashboard')
    .then(response => console.log(response.data));

axios.post('https://api.example.com/v1/data', {
    name: 'test'
});

// WebSocket 示例
const socket = new WebSocket('ws://localhost:8080/websocket');

// 其他API URL
const apiUrl = 'https://api.github.com/users';
const restEndpoint = '/rest/v2/users';
const serviceUrl = '/service/notifications';

// React/Vue 中常见的API调用
const fetchUserData = async () => {
    const response = await fetch('/api/v1/user/profile');
    return response.json();
};
