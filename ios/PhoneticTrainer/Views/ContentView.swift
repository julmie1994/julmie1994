import SwiftUI

struct ContentView: View {
    @StateObject private var engine = GameEngine()
    @State private var selectedMode: GameEngine.Mode = .practice

    private let columns = Array(repeating: GridItem(.flexible(), spacing: 8), count: 6)

    var body: some View {
        NavigationStack {
            VStack(spacing: 16) {
                modePicker
                statusCard
                controls
                letterGrid
                Spacer(minLength: 0)
            }
            .padding()
            .navigationTitle("ICAO Trainer")
        }
    }

    private var modePicker: some View {
        Picker("Mode", selection: $selectedMode) {
            ForEach(GameEngine.Mode.allCases) { mode in
                Text(mode.rawValue).tag(mode)
            }
        }
        .pickerStyle(.segmented)
    }

    private var statusCard: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                VStack(alignment: .leading) {
                    Text("Score")
                        .font(.caption)
                        .foregroundColor(.secondary)
                    Text("\(engine.score)")
                        .font(.title2)
                        .fontWeight(.semibold)
                }
                Spacer()
                VStack(alignment: .leading) {
                    Text("Highscore")
                        .font(.caption)
                        .foregroundColor(.secondary)
                    Text("\(engine.highScore)")
                        .font(.title2)
                        .fontWeight(.semibold)
                }
                Spacer()
                VStack(alignment: .leading) {
                    Text("Tempo")
                        .font(.caption)
                        .foregroundColor(.secondary)
                    Text(String(format: "%.2f", engine.activeRate))
                        .font(.title3)
                        .fontWeight(.semibold)
                }
                Spacer()
                VStack(alignment: .leading) {
                    Text("Noise")
                        .font(.caption)
                        .foregroundColor(.secondary)
                    Text(String(format: "%.2f", engine.activeNoise))
                        .font(.title3)
                        .fontWeight(.semibold)
                }
            }

            if engine.phase == .gameOver {
                Text("Game Over – try again!")
                    .foregroundColor(.red)
                    .fontWeight(.semibold)
            } else if engine.phase == .playing {
                Text("Listening...")
                    .foregroundColor(.blue)
                    .fontWeight(.semibold)
            } else if engine.phase == .awaitingInput {
                Text("Tap the letters you heard.")
                    .foregroundColor(.green)
                    .fontWeight(.semibold)
            }
        }
        .padding()
        .background(Color(.secondarySystemBackground))
        .clipShape(RoundedRectangle(cornerRadius: 16))
    }

    private var controls: some View {
        HStack(spacing: 12) {
            Button("Start") {
                engine.speedRate = selectedMode == .practice ? engine.speedRate : 0.35
                engine.noiseLevel = selectedMode == .practice ? engine.noiseLevel : 0.1
                engine.start(mode: selectedMode)
            }
            .buttonStyle(.borderedProminent)

            Button("Replay") {
                engine.replaySequence()
            }
            .buttonStyle(.bordered)
            .disabled(engine.phase == .playing || engine.phase == .idle)

            Button("Stop") {
                engine.stop()
            }
            .buttonStyle(.bordered)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .overlay(alignment: .trailing) {
            NavigationLink("Settings") {
                SettingsView(engine: engine, selectedMode: selectedMode)
            }
        }
    }

    private var letterGrid: some View {
        LazyVGrid(columns: columns, spacing: 12) {
            ForEach(PhoneticAlphabet.entries) { entry in
                Button(entry.letter) {
                    engine.handleGuess(letter: entry.letter)
                }
                .font(.title3)
                .frame(maxWidth: .infinity, minHeight: 44)
                .background(Color(.systemBackground))
                .clipShape(RoundedRectangle(cornerRadius: 10))
                .overlay(
                    RoundedRectangle(cornerRadius: 10)
                        .stroke(Color(.systemGray4), lineWidth: 1)
                )
                .disabled(engine.phase != .awaitingInput)
            }
        }
    }
}

#Preview {
    ContentView()
}
