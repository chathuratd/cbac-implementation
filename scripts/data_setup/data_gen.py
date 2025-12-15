import json
import random
import time
from datetime import datetime, timedelta
import uuid

class BehaviorDatasetGenerator:
    """Generate structured, theme-based datasets for CBAC testing"""
    
    def __init__(self):
        # Domain-specific behavior patterns organized by theme
        self.domain_behaviors = {
            "gardening": {
                "novice": [
                    "asks about basic plant care",
                    "interested in easy-to-grow plants",
                    "prefers low-maintenance flowers",
                    "seeks watering schedule advice",
                    "likes colorful beginner plants"
                ],
                "intermediate": [
                    "understands seasonal planting cycles",
                    "interested in soil composition",
                    "prefers native perennial species",
                    "discusses pest management strategies",
                    "experiments with companion planting"
                ],
                "advanced": [
                    "analyzes microclimate conditions",
                    "practices advanced propagation techniques",
                    "optimizes nutrient delivery systems",
                    "breeds hybrid plant varieties",
                    "designs complex permaculture layouts"
                ]
            },
            "cooking": {
                "novice": [
                    "follows recipes exactly",
                    "asks about basic cooking times",
                    "prefers simple one-pot meals",
                    "uses pre-made sauces",
                    "interested in microwave cooking tips"
                ],
                "intermediate": [
                    "experiments with flavor combinations",
                    "understands basic cooking chemistry",
                    "prefers making sauces from scratch",
                    "discusses knife techniques",
                    "interested in regional cuisines"
                ],
                "advanced": [
                    "creates original recipe compositions",
                    "applies molecular gastronomy principles",
                    "masters sous vide temperature control",
                    "develops signature cooking techniques",
                    "understands umami flavor building"
                ]
            },
            "programming": {
                "novice": [
                    "asks about syntax basics",
                    "interested in beginner tutorials",
                    "prefers visual programming tools",
                    "seeks step-by-step code examples",
                    "struggles with debugging concepts"
                ],
                "intermediate": [
                    "understands data structures",
                    "discusses algorithm efficiency",
                    "prefers object-oriented patterns",
                    "implements API integrations",
                    "uses version control systems"
                ],
                "advanced": [
                    "optimizes compiler performance",
                    "designs distributed architectures",
                    "implements custom algorithms",
                    "contributes to open source projects",
                    "analyzes computational complexity"
                ]
            },
            "fitness": {
                "novice": [
                    "asks about basic exercises",
                    "interested in general fitness tips",
                    "prefers simple workout routines",
                    "seeks motivation strategies",
                    "concerned about injury prevention"
                ],
                "intermediate": [
                    "tracks progressive overload",
                    "understands muscle group splits",
                    "prefers structured training programs",
                    "discusses nutrition timing",
                    "monitors form technique"
                ],
                "advanced": [
                    "periodizes training cycles",
                    "optimizes biomechanical efficiency",
                    "implements advanced recovery protocols",
                    "designs sport-specific programs",
                    "analyzes body composition metrics"
                ]
            },
            "photography": {
                "novice": [
                    "uses automatic camera modes",
                    "asks about basic composition",
                    "prefers smartphone photography",
                    "interested in filters and presets",
                    "learns basic photo editing"
                ],
                "intermediate": [
                    "understands exposure triangle",
                    "discusses lighting techniques",
                    "prefers manual camera controls",
                    "experiments with different lenses",
                    "uses RAW format workflow"
                ],
                "advanced": [
                    "masters studio lighting setups",
                    "implements advanced color grading",
                    "shoots in challenging conditions",
                    "develops signature visual style",
                    "understands optical physics"
                ]
            },
            "music": {
                "novice": [
                    "learns basic chord progressions",
                    "asks about instrument maintenance",
                    "prefers simple song structures",
                    "follows tablature notation",
                    "practices scales regularly"
                ],
                "intermediate": [
                    "understands music theory concepts",
                    "discusses harmonic analysis",
                    "prefers complex arrangements",
                    "improvises within key signatures",
                    "transcribes music by ear"
                ],
                "advanced": [
                    "composes multi-movement pieces",
                    "applies advanced modal concepts",
                    "masters polyrhythmic patterns",
                    "produces professional recordings",
                    "analyzes orchestration techniques"
                ]
            }
        }
        
        # Prompt templates that would elicit domain behaviors
        self.domain_prompts = {
            "gardening": [
                "How do I care for {plant}?",
                "What's the best way to {gardening_action}?",
                "Can you help me with {gardening_problem}?",
                "Tell me about {gardening_topic}",
                "I'm planning a {garden_type} garden"
            ],
            "cooking": [
                "How do I make {dish}?",
                "What's a good recipe for {meal_type}?",
                "Can you explain {cooking_technique}?",
                "Help me troubleshoot {cooking_problem}",
                "I want to cook {cuisine} food"
            ],
            "programming": [
                "How do I implement {programming_concept}?",
                "What's the best way to {coding_task}?",
                "Can you help debug {error_type}?",
                "Explain {programming_topic}",
                "I'm building a {project_type} application"
            ],
            "fitness": [
                "How do I improve {fitness_goal}?",
                "What's a good workout for {muscle_group}?",
                "Can you design a {training_type} program?",
                "Help me with {fitness_problem}",
                "I want to train for {fitness_event}"
            ],
            "photography": [
                "How do I photograph {subject}?",
                "What's the best {camera_setting} for {scenario}?",
                "Can you explain {photography_concept}?",
                "Help me improve {photography_skill}",
                "I'm shooting {photography_genre}"
            ],
            "music": [
                "How do I play {musical_element}?",
                "What's a good way to practice {skill}?",
                "Can you explain {music_theory}?",
                "Help me compose {music_type}",
                "I'm learning {instrument}"
            ]
        }
    
    def generate_themed_behaviors(self, domain, expertise_level, count, base_time, time_span_days):
        """Generate behaviors for a specific domain and expertise level"""
        behaviors = []
        behavior_pool = self.domain_behaviors[domain][expertise_level]
        
        for i in range(count):
            # Use behaviors from pool, with repetition if needed
            behavior_text = random.choice(behavior_pool)
            
            # Expertise level affects credibility and reinforcement
            if expertise_level == "novice":
                reinforcement_range = (1, 3)
                credibility_base = 0.60
            elif expertise_level == "intermediate":
                reinforcement_range = (3, 6)
                credibility_base = 0.75
            else:  # advanced
                reinforcement_range = (5, 8)
                credibility_base = 0.85
            
            reinforcement_count = random.randint(*reinforcement_range)
            credibility = min(0.95, credibility_base + random.uniform(-0.05, 0.10))
            
            # Stronger behaviors have higher clarity and lower decay
            clarity_score = credibility + random.uniform(-0.05, 0.10)
            extraction_confidence = credibility + random.uniform(-0.05, 0.10)
            decay_rate = 0.010 if credibility > 0.80 else 0.020
            
            # Spread timestamps across time span
            created_at = int(base_time + (i / count) * (time_span_days * 24 * 3600))
            last_seen = int(created_at + random.uniform(3600, 3600 * 24 * 5))
            
            behaviors.append({
                "behavior_id": f"beh_{uuid.uuid4().hex[:8]}",
                "behavior_text": behavior_text,
                "credibility": round(credibility, 2),
                "reinforcement_count": reinforcement_count,
                "decay_rate": round(decay_rate, 3),
                "created_at": created_at,
                "last_seen": last_seen,
                "prompt_history_ids": [],  # Will be filled later
                "clarity_score": round(min(0.98, clarity_score), 2),
                "extraction_confidence": round(min(0.98, extraction_confidence), 2),
                "session_id": f"session_{random.randint(1, 5):03d}",
                "user_id": "",  # Will be filled later
                "domain": domain,  # Ground truth for testing
                "expertise_level": expertise_level  # Ground truth for testing
            })
        
        return behaviors
    
    def generate_prompt_for_domain(self, domain, index, base_time, user_id=None):
        """Generate a prompt related to a specific domain"""
        prompt_template = random.choice(self.domain_prompts[domain])
        
        # Simple placeholder fill (domain-specific values would go here)
        prompt_text = prompt_template
        
        prompt = {
            "prompt_id": f"prompt_{index:04d}",
            "prompt_text": prompt_text,
            "timestamp": int(base_time + random.uniform(0, 3600 * 24)),
            "session_id": f"session_{random.randint(1, 5):03d}",
            "tokens": random.randint(30, 200),
            "domain": domain  # Ground truth
        }
        
        if user_id:
            prompt["user_id"] = user_id
        
        return prompt
    
    def generate_scenario_dataset(self, scenario_type, user_id=None):
        """Generate dataset for specific test scenarios"""
        if user_id is None:
            user_id = f"user_{uuid.uuid4().hex[:12]}"
        
        base_time = int(time.time()) - (3600 * 24 * 90)  # 90 days ago
        
        if scenario_type == "stable_user":
            # User with clear expertise in 3 domains
            domains_config = [
                ("gardening", "intermediate", 15),
                ("cooking", "intermediate", 12),
                ("photography", "novice", 8)
            ]
            time_span = 60
            
        elif scenario_type == "multi_domain_expert":
            # Deep expertise in multiple domains
            domains_config = [
                ("programming", "advanced", 18),
                ("music", "advanced", 15),
                ("fitness", "intermediate", 10)
            ]
            time_span = 90
            
        elif scenario_type == "expertise_evolution":
            # Progression from novice to advanced
            domains_config = [
                ("programming", "novice", 8),
                ("programming", "intermediate", 10),
                ("programming", "advanced", 12)
            ]
            time_span = 120
            
        elif scenario_type == "sparse_clusters":
            # Many small clusters
            domains_config = [
                ("gardening", "novice", 4),
                ("cooking", "novice", 4),
                ("photography", "novice", 3),
                ("fitness", "novice", 4),
                ("music", "novice", 3),
                ("programming", "novice", 4)
            ]
            time_span = 45
            
        elif scenario_type == "noisy_data":
            # Mix of high and low credibility across domains
            domains_config = [
                ("cooking", "intermediate", 10),
                ("cooking", "novice", 5),  # Contradictory signals
                ("fitness", "advanced", 8),
                ("gardening", "novice", 7)
            ]
            time_span = 60
            
        else:
            raise ValueError(f"Unknown scenario type: {scenario_type}")
        
        # Generate behaviors for each domain
        all_behaviors = []
        for domain, expertise, count in domains_config:
            behaviors = self.generate_themed_behaviors(
                domain, expertise, count, base_time, time_span
            )
            all_behaviors.extend(behaviors)
        
        # Assign user_id to all behaviors
        for b in all_behaviors:
            b["user_id"] = user_id
        
        # Sort by created_at
        all_behaviors.sort(key=lambda x: x["created_at"])
        
        # Generate prompts
        total_prompts = len(all_behaviors) * 3  # ~3 prompts per behavior
        prompts = []
        domain_list = [d[0] for d in domains_config]
        for i in range(total_prompts):
            domain = random.choice(domain_list)
            prompts.append(self.generate_prompt_for_domain(domain, i, base_time, user_id))
        
        prompts.sort(key=lambda x: x["timestamp"])
        
        # Link prompts to behaviors
        for behavior in all_behaviors:
            num_prompts = random.randint(1, 4)
            linked_prompts = random.sample(prompts, min(num_prompts, len(prompts)))
            behavior["prompt_history_ids"] = [p["prompt_id"] for p in linked_prompts]
        
        # Generate ground truth for testing
        expected_clusters = {}
        for domain, expertise, count in domains_config:
            key = f"{domain}_{expertise}"
            expected_clusters[key] = expected_clusters.get(key, 0) + count
        
        expected_domains = list(set(d[0] for d in domains_config))
        expected_core_behaviors = len([c for c in expected_clusters.values() if c >= 3])
        
        return {
            "user_id": user_id,
            "scenario_type": scenario_type,
            "prompt_histories": prompts,
            "behaviors": all_behaviors,
            "metadata": {
                "generated_at": int(time.time()),
                "total_prompts": len(prompts),
                "total_behaviors": len(all_behaviors),
                "time_span_days": time_span,
                "domains_config": domains_config
            },
            "ground_truth": {
                "expected_clusters": expected_clusters,
                "expected_domains": expected_domains,
                "expected_core_behaviors": expected_core_behaviors,
                "expertise_levels": {d: e for d, e, _ in domains_config}
            }
        }
    
    def generate_incremental_dataset(self, base_user_data, new_behaviors_config):
        """Generate incremental behaviors to add to existing user"""
        base_time = base_user_data["behaviors"][-1]["created_at"]
        user_id = base_user_data["user_id"]
        
        new_behaviors = []
        for domain, expertise, count in new_behaviors_config:
            behaviors = self.generate_themed_behaviors(
                domain, expertise, count, base_time, time_span_days=30
            )
            for b in behaviors:
                b["user_id"] = user_id
            new_behaviors.extend(behaviors)
        
        new_behaviors.sort(key=lambda x: x["created_at"])
        
        # Generate new prompts
        new_prompts = []
        for i, behavior in enumerate(new_behaviors):
            prompt = self.generate_prompt_for_domain(
                behavior["domain"], 
                len(base_user_data["prompt_histories"]) + i,
                base_time
            )
            new_prompts.append(prompt)
            behavior["prompt_history_ids"] = [prompt["prompt_id"]]
        
        return {
            "new_behaviors": new_behaviors,
            "new_prompts": new_prompts,
            "metadata": {
                "base_behavior_count": len(base_user_data["behaviors"]),
                "new_behavior_count": len(new_behaviors),
                "generated_at": int(time.time())
            }
        }
    
    def save_json(self, data, filename):
        """Save data to JSON file"""
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    def generate_db_style_datasets(self):
        """Generate database-like structure: separate behaviors and prompts collections"""
        
        print("="*70)
        print("GENERATING DB-STYLE DATASETS FOR CBAC")
        print("="*70)
        
        # Collections (like separate DB tables)
        all_behaviors = []
        all_prompts = []
        
        # Scenario definitions
        scenarios_config = {
            "stable_users": {
                "count": 3,
                "pattern": "stable_user",
                "description": "Users with clear 3-domain patterns for baseline testing"
            },
            "multi_domain_experts": {
                "count": 2,
                "pattern": "multi_domain_expert",
                "description": "Users with advanced expertise in multiple domains"
            },
            "expertise_evolution": {
                "count": 2,
                "pattern": "expertise_evolution",
                "description": "Users showing skill progression over time"
            },
            "noisy_data": {
                "count": 2,
                "pattern": "noisy_data",
                "description": "Users with contradictory signals and mixed credibility"
            },
            "sparse_clusters": {
                "count": 1,
                "pattern": "sparse_clusters",
                "description": "User with many small behavior clusters"
            }
        }
        
        # Generate all users and collect their data
        print("\n[1/4] Generating user behaviors and prompts...")
        
        all_users_metadata = []
        scenario_mappings = {}
        
        for scenario_name, config in scenarios_config.items():
            scenario_mappings[scenario_name] = []
            
            for i in range(config["count"]):
                # Generate user data
                user_id = f"user_{scenario_name}_{i+1:02d}"
                user_data = self.generate_scenario_dataset(config["pattern"], user_id)
                
                # Extract behaviors and prompts
                user_behaviors = user_data["behaviors"]
                user_prompts = user_data["prompt_histories"]
                
                # Add to collections
                all_behaviors.extend(user_behaviors)
                all_prompts.extend(user_prompts)
                
                # Store user metadata
                user_metadata = {
                    "user_id": user_id,
                    "scenario_type": config["pattern"],
                    "behavior_count": len(user_behaviors),
                    "prompt_count": len(user_prompts),
                    "ground_truth": user_data["ground_truth"],
                    "metadata": user_data["metadata"]
                }
                all_users_metadata.append(user_metadata)
                scenario_mappings[scenario_name].append(user_id)
        
        print(f"  ✓ Generated {len(all_users_metadata)} users")
        print(f"  ✓ Total Behaviors: {len(all_behaviors)}")
        print(f"  ✓ Total Prompts: {len(all_prompts)}")
        
        # Save behaviors DB
        print("\n[2/4] Saving behaviors database...")
        self.save_json(all_behaviors, "behaviors_db.json")
        print(f"  ✓ Saved {len(all_behaviors)} behaviors to behaviors_db.json")
        
        # Save prompts DB
        print("\n[3/4] Saving prompts database...")
        self.save_json(all_prompts, "prompts_db.json")
        print(f"  ✓ Saved {len(all_prompts)} prompts to prompts_db.json")
        
        # Save test scenarios with user lists
        print("\n[4/4] Generating test scenarios...")
        
        test_scenarios = []
        
        # Scenario 1: Development (small set)
        test_scenarios.append({
            "scenario_id": "dev_baseline",
            "name": "Development Baseline",
            "description": "Small controlled set for initial testing",
            "user_ids": scenario_mappings["stable_users"][:2],  # Just 2 users
            "expected_outcomes": {
                "core_behaviors_per_user": 3,
                "domains_per_user": 3,
                "min_cluster_size": 3
            }
        })
        
        # Scenario 2: Integration (full mix)
        test_scenarios.append({
            "scenario_id": "integration_full",
            "name": "Full Integration Test",
            "description": "All user types for comprehensive testing",
            "user_ids": [uid for users in scenario_mappings.values() for uid in users],
            "expected_outcomes": {
                "total_users": len(all_users_metadata),
                "varied_cluster_counts": True,
                "expertise_range": ["novice", "intermediate", "advanced"]
            }
        })
        
        # Scenario 3: Stable users only
        test_scenarios.append({
            "scenario_id": "stable_only",
            "name": "Stable Users Baseline",
            "description": "Only stable patterns for clean clustering validation",
            "user_ids": scenario_mappings["stable_users"],
            "expected_outcomes": {
                "high_confidence": True,
                "clear_clusters": True,
                "core_behaviors_per_user": 3
            }
        })
        
        # Scenario 4: Edge cases
        test_scenarios.append({
            "scenario_id": "edge_cases",
            "name": "Edge Case Testing",
            "description": "Challenging scenarios for robustness",
            "user_ids": scenario_mappings["noisy_data"] + scenario_mappings["sparse_clusters"],
            "expected_outcomes": {
                "some_low_confidence": True,
                "variable_cluster_counts": True,
                "orphan_behaviors_expected": True
            }
        })
        
        # Scenario 5: Expertise evolution
        test_scenarios.append({
            "scenario_id": "expertise_progression",
            "name": "Expertise Evolution Testing",
            "description": "Users showing skill progression over time",
            "user_ids": scenario_mappings["expertise_evolution"],
            "expected_outcomes": {
                "temporal_patterns": True,
                "expertise_level_changes": True,
                "final_expertise": "advanced"
            }
        })
        
        # Save test scenarios
        self.save_json(test_scenarios, "test_scenarios.json")
        print(f"  ✓ Saved {len(test_scenarios)} test scenarios to test_scenarios.json")
        
        # Save users metadata (includes ground truth)
        self.save_json(all_users_metadata, "users_metadata.json")
        print(f"  ✓ Saved user metadata to users_metadata.json")
        
        # Generate incremental test data
        print("\n[BONUS] Generating incremental update scenario...")
        
        # Pick first stable user
        base_user_id = scenario_mappings["stable_users"][0]
        base_behaviors = [b for b in all_behaviors if b["user_id"] == base_user_id]
        base_prompts = [p for p in all_prompts if p["user_id"] == base_user_id]
        
        # Generate new behaviors for incremental update
        base_time = max(b["created_at"] for b in base_behaviors)
        
        # New behaviors: 5 in existing domain, 4 in new domain
        new_gardening = self.generate_themed_behaviors("gardening", "intermediate", 5, base_time, 30)
        new_programming = self.generate_themed_behaviors("programming", "novice", 4, base_time, 30)
        
        incremental_behaviors = new_gardening + new_programming
        for b in incremental_behaviors:
            b["user_id"] = base_user_id
        
        # Generate new prompts
        incremental_prompts = []
        for i, behavior in enumerate(incremental_behaviors):
            prompt_id = f"prompt_incr_{i:04d}"
            prompt = self.generate_prompt_for_domain(
                behavior["domain"],
                9999 + i,  # High index to avoid conflicts
                base_time
            )
            prompt["prompt_id"] = prompt_id
            prompt["user_id"] = base_user_id
            incremental_prompts.append(prompt)
            behavior["prompt_history_ids"] = [prompt_id]
        
        incremental_scenario = {
            "scenario_id": "incremental_update",
            "name": "Incremental Clustering Test",
            "description": "Add new behaviors to existing user, test incremental processing",
            "base_user_id": base_user_id,
            "base_state": {
                "behavior_count": len(base_behaviors),
                "prompt_count": len(base_prompts),
                "established_domains": ["gardening", "cooking", "photography"]
            },
            "incremental_behaviors": incremental_behaviors,
            "incremental_prompts": incremental_prompts,
            "expected_outcomes": {
                "new_behavior_count": len(incremental_behaviors),
                "gardening_cluster_should_grow": True,
                "programming_cluster_should_form": True,
                "no_full_reclustering": True
            }
        }
        
        self.save_json(incremental_scenario, "test_scenario_incremental.json")
        print(f"  ✓ Saved incremental scenario with {len(incremental_behaviors)} new behaviors")
        
        # Print summary
        print("\n" + "="*70)
        print("SUMMARY")
        print("="*70)
        print(f"\n✓ Database Files:")
        print(f"  - behaviors_db.json ({len(all_behaviors)} behaviors)")
        print(f"  - prompts_db.json ({len(all_prompts)} prompts)")
        print(f"  - users_metadata.json ({len(all_users_metadata)} users)")
        print(f"\n✓ Test Scenarios:")
        print(f"  - test_scenarios.json ({len(test_scenarios)} scenarios)")
        print(f"  - test_scenario_incremental.json (1 incremental test)")
        print(f"\n✓ User Distribution:")
        for scenario_name, user_ids in scenario_mappings.items():
            print(f"  - {scenario_name}: {len(user_ids)} users")
        
        # Show sample data
        print("\n" + "="*70)
        print("SAMPLE DATA")
        print("="*70)
        
        print("\n--- Sample Behavior (from behaviors_db.json) ---")
        sample_behavior = all_behaviors[0].copy()
        sample_behavior.pop("domain", None)  # Remove ground truth
        sample_behavior.pop("expertise_level", None)
        print(json.dumps(sample_behavior, indent=2))
        
        print("\n--- Sample Prompt (from prompts_db.json) ---")
        sample_prompt = all_prompts[0].copy()
        sample_prompt.pop("domain", None)  # Remove ground truth
        print(json.dumps(sample_prompt, indent=2))
        
        print("\n--- Sample Test Scenario ---")
        print(json.dumps(test_scenarios[0], indent=2))
        
        print("\n" + "="*70)
        print("✓ ALL DATASETS GENERATED SUCCESSFULLY!")
        print("="*70)


# Example usage
if __name__ == "__main__":
    generator = BehaviorDatasetGenerator()
    generator.generate_db_style_datasets()