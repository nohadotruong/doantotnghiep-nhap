"""
Configuration presets for different TSP problem sizes and optimization strategies
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class PSO_Config:
    """PSO configuration preset"""
    name: str
    n_particles: int
    max_iterations: int
    w: float  # inertia weight
    c1: float  # cognitive parameter
    c2: float  # social parameter
    description: str


# Presets for different problem sizes and strategies
PRESETS: Dict[str, PSO_Config] = {
    # Quick & dirty - for testing/small problems
    'quick': PSO_Config(
        name='Quick',
        n_particles=20,
        max_iterations=200,
        w=0.7,
        c1=1.5,
        c2=1.5,
        description='Nhanh chóng, phù hợp cho bài toán nhỏ dưới 20 thành phố'
    ),
    
    # Balanced - good trade-off between speed and quality
    'balanced': PSO_Config(
        name='Balanced',
        n_particles=30,
        max_iterations=500,
        w=0.7,
        c1=1.5,
        c2=1.5,
        description='Cân bằng giữa tốc độ và chất lượng, phù hợp nhất cho hầu hết bài toán'
    ),
    
    # Thorough - for better quality solutions
    'thorough': PSO_Config(
        name='Thorough',
        n_particles=50,
        max_iterations=1000,
        w=0.7,
        c1=2.0,
        c2=2.0,
        description='Kỹ lưỡng, tìm kiếm lâu hơn nhưng chất lượng tốt hơn'
    ),
    
    # Exploration-focused - emphasize exploration over exploitation
    'exploration': PSO_Config(
        name='Exploration',
        n_particles=40,
        max_iterations=800,
        w=0.9,  # high inertia for exploration
        c1=1.2,
        c2=1.2,
        description='Tập trung vào khám phá không gian tìm kiếm rộng'
    ),
    
    # Exploitation-focused - emphasize exploitation over exploration
    'exploitation': PSO_Config(
        name='Exploitation',
        n_particles=35,
        max_iterations=600,
        w=0.4,  # low inertia for exploitation
        c1=2.5,
        c2=2.5,
        description='Tập trung vào khai thác vùng tốt, ít khám phá hơn'
    ),
    
    # Very large problems
    'large_scale': PSO_Config(
        name='Large Scale',
        n_particles=100,
        max_iterations=2000,
        w=0.7,
        c1=1.5,
        c2=1.5,
        description='Cho bài toán lớn với 50-200+ thành phố'
    ),
    
    # Ultra-fast for real-time scenarios
    'ultra_fast': PSO_Config(
        name='Ultra Fast',
        n_particles=15,
        max_iterations=100,
        w=0.7,
        c1=1.5,
        c2=1.5,
        description='Cực nhanh, dành cho các tình huống yêu cầu kết quả ngay lập tức'
    ),
    
    # Conservative - focus on reliability
    'conservative': PSO_Config(
        name='Conservative',
        n_particles=25,
        max_iterations=400,
        w=0.8,
        c1=1.7,
        c2=1.7,
        description='Bảo thủ, ưu tiên độ tin cậy và ổn định'
    ),
}


def get_preset(name: str) -> PSO_Config:
    """
    Get a preset configuration by name
    
    Args:
        name: Name of the preset (key in PRESETS)
        
    Returns:
        PSO_Config instance
        
    Raises:
        ValueError: If preset name not found
    """
    if name not in PRESETS:
        available = ', '.join(PRESETS.keys())
        raise ValueError(f"Preset '{name}' không tìm thấy. Các preset có sẵn: {available}")
    return PRESETS[name]


def list_presets():
    """Print all available presets"""
    print("\n" + "="*70)
    print("Available Presets for TSP-PSO")
    print("="*70)
    for key, config in PRESETS.items():
        print(f"\n[{key.upper()}] {config.name}")
        print(f"  {config.description}")
        print(f"  Particles: {config.n_particles}, Iterations: {config.max_iterations}")
        print(f"  w={config.w}, c1={config.c1}, c2={config.c2}")
    print("\n" + "="*70)


def create_pso_with_preset(problem, preset_name: str):
    """
    Create a PSO instance with a named preset
    
    Args:
        problem: TSPProblem instance
        preset_name: Name of preset
        
    Returns:
        PSO instance
    """
    from tsp_pso import PSO
    
    config = get_preset(preset_name)
    
    return PSO(
        problem,
        n_particles=config.n_particles,
        max_iterations=config.max_iterations,
        w=config.w,
        c1=config.c1,
        c2=config.c2
    )


if __name__ == "__main__":
    # Display all presets
    list_presets()
    
    # Example: Use a preset
    print("\nExample: Solving TSP with 'balanced' preset")
    print("-" * 70)
    
    from tsp_pso import TSPProblem, generate_cities
    
    # Generate problem
    cities = generate_cities(20, seed=42)
    problem = TSPProblem(cities)
    
    # Create PSO with preset
    pso = create_pso_with_preset(problem, 'balanced')
    best_tour, best_distance, history = pso.solve()
    
    print(f"\nResult with 'balanced' preset:")
    print(f"  Best distance: {best_distance:.2f}")
