const like_form = document.querySelector('#like-form');

if (like_form) {
    like_form.addEventListener('submit', (e) => {
        e.preventDefault();
        toggleLike();
    });
}

async function toggleLike() {
    const url = like_form.action;
    const csrftoken = like_form.querySelector("[name='csrfmiddlewaretoken']").value;
    const response = await fetch(url, {
        method: 'POST',
        headers: {'X-CSRFToken': csrftoken},
        mode: 'same-origin' // Do not send CSRF token to another domain.
    });
    const json = await response.json();
    document.querySelector('#liked-icon').classList.toggle('d-none');
    document.querySelector('#not-liked-icon').classList.toggle('d-none');
    document.querySelector('#likes-count').innerHTML = json.likes_count;
}