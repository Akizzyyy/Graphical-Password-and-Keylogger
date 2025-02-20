package com.example.password_project.Controllers;

import com.example.password_project.models.User;
import com.example.password_project.services.UserService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

@RestController
@RequestMapping("/auth")
@CrossOrigin(origins = "http://localhost:63342")
public class AuthController {
    private final UserService userService;

    public AuthController(UserService userService) {
        this.userService = userService;
    }

    // ✅ Register a new user (JSON Payload)
    @PostMapping("/register")
    public ResponseEntity<Map<String, Object>> registerUser(@RequestBody User user) {
        Map<String, Object> response = new HashMap<>();

        if (userService.findByUsername(user.getUsername()).isPresent()) {
            response.put("success", false);
            response.put("message", "Username already exists!");
            return ResponseEntity.badRequest().body(response);
        }

        userService.saveUser(user);
        response.put("success", true);
        response.put("message", "User registered successfully!");
        return ResponseEntity.ok(response);
    }

    @PostMapping("/login")
    public ResponseEntity<Map<String, Object>> login(@RequestBody User user) {
        Map<String, Object> response = new HashMap<>();

        Optional<User> authenticatedUser = userService.authenticate(user.getUsername(), user.getPassword());

        if (authenticatedUser.isPresent()) {
            response.put("success", true);
            response.put("message", "Login successful!");
            return ResponseEntity.ok(response);
        } else {
            response.put("success", false);
            response.put("message", "Invalid username or password!");
            return ResponseEntity.status(401).body(response);
        }
    }
}