const USERS_STORAGE_KEY = 'smart_lock_users';

export const getUsers = () => {
  const users = localStorage.getItem(USERS_STORAGE_KEY);
  return users ? JSON.parse(users) : [];
};

export const registerUser = (username, password) => {
  const users = getUsers();
  
  // Check if username already exists
  if (users.some(user => user.username === username)) {
    throw new Error('Username already exists');
  }

  // Add new user
  users.push({ username, password });
  localStorage.setItem(USERS_STORAGE_KEY, JSON.stringify(users));
};

export const loginUser = (username, password) => {
  const users = getUsers();
  const user = users.find(u => u.username === username && u.password === password);
  
  if (!user) {
    throw new Error('Invalid username or password');
  }

  // Store current user in session
  sessionStorage.setItem('currentUser', username);
  return user;
};

export const isAuthenticated = () => {
  return sessionStorage.getItem('currentUser') !== null;
};

export const logout = () => {
  sessionStorage.removeItem('currentUser');
};