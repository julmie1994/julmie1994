import XCTest
@testable import PhoneticTrainer

@MainActor
final class GameEngineTests: XCTestCase {
    func testHighscoreIncreasesWhenScoring() async {
        let speech = SpeechServiceStub()
        let noise = NoiseServiceStub()
        let engine = GameEngine(speechService: speech, noiseService: noise, configureAudioSession: false)

        engine.start(mode: .practice)
        engine.setSequenceForTesting([PhoneticEntry(letter: "A", word: "Alpha")])
        engine.setPhaseForTesting(.awaitingInput)
        engine.handleGuess(letter: "A")

        XCTAssertEqual(engine.score, 1)
        XCTAssertEqual(engine.highScore, 1)
    }

    func testHighscoreModeScalesDifficulty() async {
        let speech = SpeechServiceStub()
        let noise = NoiseServiceStub()
        let engine = GameEngine(speechService: speech, noiseService: noise, configureAudioSession: false)

        engine.start(mode: .highscore)
        engine.setSequenceForTesting([PhoneticEntry(letter: "B", word: "Bravo")])
        engine.setPhaseForTesting(.awaitingInput)
        engine.handleGuess(letter: "B")

        XCTAssertGreaterThan(engine.activeRate, 0.4)
        XCTAssertGreaterThan(engine.activeNoise, 0.0)
    }
}

final class SpeechServiceStub: SpeechServiceProtocol {
    func stop() {}
    func speakSequence(words: [String], rate: Float) async {}
}

final class NoiseServiceStub: NoiseServiceProtocol {
    func start(volume: Float) {}
    func updateVolume(_ volume: Float) {}
    func stop() {}
}
