import AVFoundation

protocol SpeechServiceProtocol: AnyObject {
    func stop()
    func speakSequence(words: [String], rate: Float) async
}

final class SpeechService: NSObject, AVSpeechSynthesizerDelegate, SpeechServiceProtocol {
    private let synthesizer = AVSpeechSynthesizer()
    private var continuation: CheckedContinuation<Void, Never>?

    override init() {
        super.init()
        synthesizer.delegate = self
    }

    func stop() {
        synthesizer.stopSpeaking(at: .immediate)
    }

    func speakSequence(words: [String], rate: Float) async {
        for word in words {
            await speak(word: word, rate: rate)
            try? await Task.sleep(nanoseconds: 180_000_000)
        }
    }

    private func speak(word: String, rate: Float) async {
        await withCheckedContinuation { continuation in
            self.continuation = continuation
            let utterance = AVSpeechUtterance(string: word)
            utterance.voice = AVSpeechSynthesisVoice(language: "en-US")
            utterance.rate = rate
            utterance.pitchMultiplier = 1.0
            utterance.volume = 1.0
            synthesizer.speak(utterance)
        }
    }

    func speechSynthesizer(_ synthesizer: AVSpeechSynthesizer, didFinish utterance: AVSpeechUtterance) {
        continuation?.resume()
        continuation = nil
    }

    func speechSynthesizer(_ synthesizer: AVSpeechSynthesizer, didCancel utterance: AVSpeechUtterance) {
        continuation?.resume()
        continuation = nil
    }
}
