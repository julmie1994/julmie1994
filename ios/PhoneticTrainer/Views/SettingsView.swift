import SwiftUI

struct SettingsView: View {
    @ObservedObject var engine: GameEngine
    let selectedMode: GameEngine.Mode

    var body: some View {
        Form {
            Section("Mode") {
                Text(selectedMode == .practice ? "Practice settings" : "Highscore increases speed + noise automatically.")
                    .font(.subheadline)
                    .foregroundColor(.secondary)
            }

            if selectedMode == .practice {
                Section("Speech") {
                    Slider(value: $engine.speedRate, in: 0.2...0.6, step: 0.02) {
                        Text("Speed")
                    } minimumValueLabel: {
                        Text("Slow")
                    } maximumValueLabel: {
                        Text("Fast")
                    }
                    Text(String(format: "Current: %.2f", engine.speedRate))
                        .font(.caption)
                        .foregroundColor(.secondary)
                }

                Section("ATC Noise") {
                    Slider(value: $engine.noiseLevel, in: 0.0...0.8, step: 0.05) {
                        Text("Noise")
                    } minimumValueLabel: {
                        Text("Off")
                    } maximumValueLabel: {
                        Text("Max")
                    }
                    Text(String(format: "Current: %.2f", engine.noiseLevel))
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            } else {
                Section("Highscore scaling") {
                    Text("Each correct round adds speed and noise.")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                    Text(String(format: "Starting speed: %.2f", engine.activeRate))
                        .font(.caption)
                        .foregroundColor(.secondary)
                    Text(String(format: "Starting noise: %.2f", engine.activeNoise))
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
        }
        .navigationTitle("Settings")
    }
}

#Preview {
    SettingsView(engine: GameEngine(), selectedMode: .practice)
}
