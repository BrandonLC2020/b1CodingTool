import SwiftUI

struct ViewTemplate: View {
    // MARK: - Properties
    @State private var isLoading = false
    
    // MARK: - Body
    var body: some View {
        NavigationStack {
            VStack(spacing: 20) {
                Text("Hello, b1CodingTool!")
                    .font(.title)
                
                if isLoading {
                    ProgressView()
                }
                
                Button("Action") {
                    isLoading.toggle()
                }
                .buttonStyle(.borderedProminent)
            }
            .padding()
            .navigationTitle("Template")
        }
    }
}

// MARK: - Previews
#Preview {
    ViewTemplate()
}
