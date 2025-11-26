package org.example;

public class App {
    public static void main(String[] args) {
        String name = "Raza";

        // INTENTIONAL ERROR: missing closing quote
        System.out.println("Hello " + name);

        // This will break compilation
        System.out.println("broken line);
    }
}
