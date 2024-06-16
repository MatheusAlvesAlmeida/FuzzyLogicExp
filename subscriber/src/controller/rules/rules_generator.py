import random
import sys
import math
import numpy as np
import pandas as pd

sys.path.append('/home/matheus/Documentos/GIT/FuzzyLogicExp/subscriber/src')
from controller.fuzzy_controller import FuzzyController
from controller.rules.const import INITIAL_POPULATION

class GeneticAlgorithm:
    @staticmethod
    def crossover(parent1, parent2):
        # Ensure the parents have the same length
        if len(parent1) != len(parent2):
            raise ValueError("Parent rule sets must have the same length")

        # Choose a random crossover point
        crossover_point = random.randint(1, len(parent1) - 1)

        # Create offspring by combining rules from parents at the crossover point
        offspring1 = parent1[:crossover_point] + parent2[crossover_point:]
        offspring2 = parent2[:crossover_point] + parent1[crossover_point:]

        return offspring1, offspring2

    @staticmethod
    def roulette_wheel_selection(population, fitness_scores):
        total_fitness = sum(fitness_scores)
        selection_probs = [f / total_fitness for f in fitness_scores]

        # Generate cumulative probabilities
        cumulative_probs = []
        cumulative_sum = 0.0
        for prob in selection_probs:
            cumulative_sum += prob
            cumulative_probs.append(cumulative_sum)

        def select_one():
            r = random.random()
            for i, cum_prob in enumerate(cumulative_probs):
                if r <= cum_prob:
                    return population[i]

        # Select two parents
        parent1 = select_one()
        parent2 = select_one()

        return parent1, parent2

    @staticmethod
    def mutate(parent, mutation_rate):
        pca_labels = ['higher_decrease', 'medium_decrease', 'small_decrease',
                      'zero', 'small_increase', 'medium_increase', 'higher_increase']
        mutated = parent.copy()
        for i in range(len(mutated)):
            if random.random() < mutation_rate:
                antecedent, consequent = mutated[i].split(' THEN ')
                error_level = antecedent.split('= ')[1].strip()
                pca_level = consequent.split('= ')[1].strip()
                error_index = ['negative_large', 'negative_medium', 'negative_small', 'zero',
                               'positive_small', 'positive_medium', 'positive_large'].index(error_level)
                pca_index = pca_labels.index(pca_level)
                error_index = (error_index + random.randint(-1, 1)) % 7
                pca_index = (pca_index + random.randint(-1, 1)) % 7
                mutated[i] = f"IF ERROR = {error_level} THEN PCA = {pca_labels[pca_index]}"
        return mutated

    @staticmethod
    def calculate_fitness_from_df(rule_set, df, df_reference, lower_bound, upper_bound, setpoint):
        controller = FuzzyController(setpoint)
        controller.update_rules(rule_set)

        df['controller_output'] = controller.simulate(df['error'])
        df['new_prefetch_count'] = round(df['controller_output'] + df['prefetch_count'])
        df['new_prefetch_count'] = df['new_prefetch_count'].apply(lambda x: lower_bound if x < lower_bound else x)
        df['new_prefetch_count'] = df['new_prefetch_count'].apply(lambda x: upper_bound if x > upper_bound else x)

        df['new_arrival_rate'] = df['new_prefetch_count'].map(df_reference['arrival_rate'])
        
        max_arrival_rate = df_reference['arrival_rate'].max()
        min_arrival_rate = df_reference['arrival_rate'].min()
        df['deviation'] = df['new_arrival_rate'] - setpoint
        df['mse'] = df['deviation'] ** 2
        mse = df['mse'].mean()
        rmse = math.sqrt(mse)
        nrmse = rmse / (max_arrival_rate - min_arrival_rate)

        return nrmse
    
    def improve_rules(self, setpoint):
        initial_population = INITIAL_POPULATION
        df = pd.read_csv('results.csv')
        df_reference = df.groupby('prefetch_count').mean().drop(columns=['sample_number', 'setpoint'])
        df['error'] = df['arrival_rate'] - setpoint 
        lower_bound = df['prefetch_count'].min()
        upper_bound = df['prefetch_count'].max()

        best_fitness = math.inf

        for generation in range(100):
            # Calculate the fitness of each individual in the population
            fitness_scores = []
            for rule_set in initial_population:
                fitness = self.calculate_fitness_from_df(rule_set, df, df_reference,lower_bound, upper_bound, setpoint)
                fitness_scores.append(fitness)

            # Find the best individual in the population
            best_index = np.argmin(fitness_scores)
            best_rule_set = initial_population[best_index]
            best_fitness = fitness_scores[best_index]

            # Check if the best fitness is less than 0.2
            if best_fitness < 0.2:
                break

            # Select parents for crossover
            parent1, parent2 = self.roulette_wheel_selection(initial_population, fitness_scores)

            # Perform crossover to generate offspring
            offspring1, offspring2 = self.crossover(parent1, parent2)

            # Mutate the offspring
            offspring1 = self.mutate(offspring1, 0.3)
            offspring2 = self.mutate(offspring2, 0.3)

            # Replace the worst individual in the population with the offspring
            worst_index = np.argmax(fitness_scores)
            initial_population[worst_index] = offspring1
            worst_index = np.argmax(fitness_scores)
            initial_population[worst_index] = offspring2

            print(f"Generation {generation}: Best Fitness = {best_fitness}")

        return best_rule_set