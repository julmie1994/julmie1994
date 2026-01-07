import AVFoundation

protocol NoiseServiceProtocol: AnyObject {
    func start(volume: Float)
    func updateVolume(_ volume: Float)
    func stop()
}

final class NoiseService: NoiseServiceProtocol {
    private let engine = AVAudioEngine()
    private let sourceNode: AVAudioSourceNode
    private let format: AVAudioFormat
    private var currentVolume: Float = 0.0

    init() {
        let sampleRate = 44_100.0
        format = AVAudioFormat(standardFormatWithSampleRate: sampleRate, channels: 1)!
        sourceNode = AVAudioSourceNode { _, _, frameCount, audioBufferList -> OSStatus in
            let ablPointer = UnsafeMutableAudioBufferListPointer(audioBufferList)
            for buffer in ablPointer {
                guard let pointer = buffer.mData?.assumingMemoryBound(to: Float.self) else { continue }
                for frame in 0..<Int(frameCount) {
                    pointer[frame] = Float.random(in: -1...1)
                }
            }
            return noErr
        }

        engine.attach(sourceNode)
        engine.connect(sourceNode, to: engine.mainMixerNode, format: format)
    }

    func start(volume: Float) {
        currentVolume = volume
        engine.mainMixerNode.outputVolume = currentVolume

        if !engine.isRunning {
            do {
                try engine.start()
            } catch {
                print("Failed to start noise engine: \(error)")
            }
        }
    }

    func updateVolume(_ volume: Float) {
        currentVolume = volume
        engine.mainMixerNode.outputVolume = currentVolume
    }

    func stop() {
        engine.stop()
        currentVolume = 0.0
    }
}
