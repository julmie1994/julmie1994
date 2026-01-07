import Foundation
import AVFoundation

@MainActor
final class GameEngine: ObservableObject {
    enum Phase {
        case idle
        case playing
        case awaitingInput
        case gameOver
    }

    enum Mode: String, CaseIterable, Identifiable {
        case practice = "Practice"
        case highscore = "Highscore"

        var id: String { rawValue }
    }

    @Published private(set) var sequence: [PhoneticEntry] = []
    @Published private(set) var phase: Phase = .idle
    @Published private(set) var currentIndex: Int = 0
    @Published private(set) var score: Int = 0
    @Published private(set) var highScore: Int = UserDefaults.standard.integer(forKey: "highScore")
    @Published var speedRate: Float = 0.4
    @Published var noiseLevel: Float = 0.0
    @Published private(set) var activeRate: Float = 0.4
    @Published private(set) var activeNoise: Float = 0.0

    private let speechService: SpeechServiceProtocol
    private let noiseService: NoiseServiceProtocol
    private let shouldConfigureAudioSession: Bool
    private var mode: Mode = .practice
    private var roundLength: Int = 3

    init(
        speechService: SpeechServiceProtocol = SpeechService(),
        noiseService: NoiseServiceProtocol = NoiseService(),
        configureAudioSession: Bool = true
    ) {
        self.speechService = speechService
        self.noiseService = noiseService
        self.shouldConfigureAudioSession = configureAudioSession
    }

    func start(mode: Mode) {
        self.mode = mode
        score = 0
        roundLength = 3
        activeRate = speedRate
        activeNoise = noiseLevel
        if shouldConfigureAudioSession {
            configureAudioSession()
        }
        nextRound()
    }

    func stop() {
        speechService.stop()
        noiseService.stop()
        phase = .idle
    }

    func handleGuess(letter: String) {
        guard phase == .awaitingInput else { return }
        let expected = sequence[currentIndex].letter
        if letter == expected {
            currentIndex += 1
            if currentIndex >= sequence.count {
                score += 1
                if score > highScore {
                    highScore = score
                    UserDefaults.standard.set(highScore, forKey: "highScore")
                }
                adjustDifficultyForHighscore()
                nextRound()
            }
        } else {
            phase = .gameOver
            noiseService.stop()
        }
    }

    func replaySequence() {
        Task { await playSequence() }
    }

#if DEBUG
    func setSequenceForTesting(_ entries: [PhoneticEntry]) {
        sequence = entries
        currentIndex = 0
    }

    func setPhaseForTesting(_ phase: Phase) {
        self.phase = phase
    }
#endif

    private func nextRound() {
        sequence = (0..<roundLength).map { _ in PhoneticAlphabet.entries.randomElement()! }
        currentIndex = 0
        Task { await playSequence() }
    }

    private func adjustDifficultyForHighscore() {
        guard mode == .highscore else { return }
        roundLength = min(roundLength + 1, 7)
        activeRate = min(activeRate + 0.02, 0.6)
        activeNoise = min(activeNoise + 0.05, 0.8)
    }

    private func playSequence() async {
        phase = .playing
        let words = sequence.map { $0.word }
        noiseService.start(volume: activeNoise)
        await speechService.speakSequence(words: words, rate: activeRate)
        phase = .awaitingInput
    }

    private func configureAudioSession() {
        let session = AVAudioSession.sharedInstance()
        do {
            try session.setCategory(.playback, mode: .spokenAudio, options: [.duckOthers])
            try session.setActive(true, options: .notifyOthersOnDeactivation)
        } catch {
            print("Failed to configure audio session: \(error)")
        }
    }
}
