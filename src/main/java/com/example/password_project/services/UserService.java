package com.example.password_project.services;

import com.example.password_project.models.User;
import com.example.password_project.repositories.UserRepository;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Service;

import java.util.Optional;

@Service
public class UserService {
    private final UserRepository userRepository;
    private final BCryptPasswordEncoder passwordEncoder;

    public UserService(UserRepository userRepository) {
        this.userRepository = userRepository;
        this.passwordEncoder = new BCryptPasswordEncoder();
    }

    // ✅ Save a new user
    public User saveUser(User user) {
        user.setPassword(passwordEncoder.encode(user.getPassword()));
        return userRepository.save(user);
    }

    // ✅ Find a user by username
    public Optional<User> findByUsername(String username) {
        return userRepository.findByUsername(username);
    }

    // ✅ Register a user (alternative method)
    public User registerUser(String username, String password) {
        String hashedPassword = passwordEncoder.encode(password);
        User user = new User(username, hashedPassword);
        return userRepository.save(user);
    }

    // ✅ Authenticate user (login)
    public Optional<User> authenticate(String username, String password) {
        Optional<User> user = userRepository.findByUsername(username);
        return user.filter(u -> passwordEncoder.matches(password, u.getPassword()));
    }
}
