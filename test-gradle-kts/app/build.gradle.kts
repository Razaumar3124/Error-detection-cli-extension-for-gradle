plugins {
    application
}

repositories {
    mavenCentral()
}

dependencies {
    testImplementation(libs.junit)
    implementation(libs.guava)
}

java {
    toolchain {
        languageVersion = JavaLanguageVersion.of(21)
    }
}

tasks.withType<JavaCompile>().configureEach {

    // ====================================================
    // FORCE FULL RECOMPILE (ABSOLUTE REQUIREMENT)
    // ====================================================
    outputs.upToDateWhen { false }  // always recompile

    // ====================================================
    // Multi-error mode (collect ALL errors)
    // ====================================================
    options.compilerArgs.add("-Xmaxerrs")
    options.compilerArgs.add("500")
    options.compilerArgs.add("-Xdiags:verbose")
    options.compilerArgs.add("-XDshouldStopPolicy=NEVER")
    options.compilerArgs.add("-Xlint:all")

    // ====================================================
    // Gradle 9.x — disable indirect incremental mechanisms
    // ====================================================
    options.compilerArgs.add("-Xprefer:source")  
    options.compilerArgs.add("-XDignore.symbol.file")

    // Encoding
    options.encoding = "UTF-8"

    // IMPORTANT: let the build continue after errors
    options.isFailOnError = false
}

application {
    mainClass = "org.example.App"
}
