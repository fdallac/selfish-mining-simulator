def single_selfish_attack_simu(q, g, D, T, bitcoin_value, bitcoin_reward):
    
    # INPUT
    # q : relative hashrate
    # g : fraction of the network connected with the attacker
    # D : maximum authorized delay
    # T : exit time
    # bitcoin_value : coinbase
    # bitcoin_reward : no. of bitcoin for each block mined

    # OUTPUT
    # [revenue, elapsed time, official_chain, orphan_blocks, mining_diff]

    import random as rnd
    rnd.seed()

    # data
    mining_reward = bitcoin_value * bitcoin_reward # USD for each block fairly mined
    mining_time = 600 # seconds

    # vars
    revenue = 0 # USD
    official_chain = 0 # n of blocks
    secret_fork = 0 # n of blocks
    honest_fork = 0 # n of blocks
    orphan_blocks = 0 # n of blocks
    elapsed_time = 0 # seconds
    updating_time = 0 # seconds
    updating_counter = 0 # blocks
    default_time = 3600 * 24 * 7 * 2 # seconds

    # story lists
    time_story = [0]
    revr_story = [bitcoin_value * bitcoin_reward * q / 600]
    diff_story = [1]

    while (elapsed_time < T):
        # algo: premining
        while (True):
            # difficulty update
            if (updating_counter >= 2016): 
                mining_time = mining_time * (default_time / updating_time)
                updating_counter = 0
                updating_time = 0
                # print("DIFFICULTY UPDATED -> new avg mining time =", mining_time, "s") # DEBUG

                time_story.append(elapsed_time)
                revr_story.append(revenue / elapsed_time)
                diff_story.append(mining_time / 600)

            elapsed_time += mining_time
            updating_time += mining_time

            # attacker mines a block
            if (rnd.random() < q): 
                secret_fork += 1
                # print("Attacker mines a block -> secret fork =", secret_fork) # DEBUG
                # print("SELFISH ATTACK BEGINS") # DEBUG
                break
            # honest miners mine a block
            else: 
                official_chain += 1
                updating_counter += 1
                # print("Honest miners mine a block -> blockchain =", official_chain) # DEBUG

        # algo: selfish mining attack
        while (True):
            # difficulty_update
            if (updating_counter >= 2016): 
                mining_time = mining_time * (default_time / updating_time)
                updating_counter = 0
                updating_time = 0
                # print("DIFFICULTY UPDATED -> new avg mining time =", mining_time, "s") # DEBUG

                time_story.append(elapsed_time)
                revr_story.append(revenue / elapsed_time)
                diff_story.append(mining_time / 600)

            elapsed_time += mining_time
            updating_time += mining_time

            # attacker mines a block
            if (rnd.random() < q): 
                secret_fork += 1
                # print("Attacker mines a block -> secret fork =", secret_fork) # DEBUG
            # honest miners mine a block   
            else:               
                honest_fork += 1
                updating_counter += 1
                # print("Honest miners mine a block -> honest fork =", honest_fork) # DEBUG

                # advantage of one block: attacker releases his fork
                if (secret_fork - honest_fork == 1): 
                    official_chain += secret_fork
                    orphan_blocks += honest_fork
                    revenue += secret_fork * mining_reward
                    secret_fork = 0
                    honest_fork = 0
                    updating_counter += 1
                    # print("Attacker releases his fork -> blockchain =", official_chain) # DEBUG
                    # print("Attacker's gain =", revenue, "USD") # DEBUG
                    # print("SELFISH ATTACK ENDS") # DEBUG
                    break

                # competition between forks
                elif (secret_fork - honest_fork == 0):
                    updating_counter += 1
                    # print("COMPETITION ON THE TOP OF THE FORK") # DEBUG
                    # attacker mines a block on the top of his fork and he realises all
                    if (rnd.random() < q):
                        official_chain += (secret_fork + 1)
                        orphan_blocks += honest_fork
                        revenue += (secret_fork + 1) * mining_reward
                        secret_fork = 0
                        honest_fork = 0
                        # print("Attacker mines on the top of his fork -> blockchain =", official_chain) # DEBUG
                        # print("Attacker's gain =", revenue, "USD") # DEBUG
                        # print("SELFISH ATTACK ENDS") # DEBUG
                        break
                    else:
                        # honest miners mine a block on the top of the attacker fork
                        if (rnd.random() < g):
                            official_chain += (secret_fork + 1)
                            orphan_blocks += honest_fork
                            revenue += secret_fork * mining_reward
                            secret_fork = 0
                            honest_fork = 0
                            # print("Honest miners mine a block on the top of the attacker fork -> blockchain =", official_chain) # DEBUG
                            # print("Attacker's gain =", revenue, "USD") # DEBUG
                            # print("SELFISH ATTACK ENDS") # DEBUG
                            break
                        # honest miners mine a block on the top of the honest fork    
                        else:
                            official_chain += (honest_fork + 1)
                            orphan_blocks += secret_fork
                            secret_fork = 0
                            honest_fork = 0
                            # print("Honest miners mine a blokc on the top of the honest fork -> blockchain =", official_chain) # DEBUG
                            # print("SELFISH ATTACK ENDS") # DEBUG
                            break 

                # attack is over
                elif (secret_fork - honest_fork < -D): 
                    official_chain += honest_fork
                    orphan_blocks += secret_fork
                    secret_fork = 0
                    honest_fork = 0
                    # print("Attacker gives up") # DEBUG  
                    #print("SELFISH ATTACK ENDS") # DEBUG
                    break

    time_story.append(elapsed_time)
    revr_story.append(revenue / elapsed_time)
    diff_story.append(mining_time / 600)

    return revenue, time_story, revr_story, diff_story, orphan_blocks



def attack_simu_rescaling(revr_story, diff_story, time_story, time_scale):
    rescaled_revr_story = []
    rescaled_diff_story = []
    j = 0 

    for i in range(len(time_scale)):
        while(time_story[j] < time_scale[i]):
            j += 1  
        if (time_scale[i] == time_story[j]):
            rescaled_revr_story.append(revr_story[j])
            rescaled_diff_story.append(diff_story[j])
        else:
            rescaled_revr_story.append((revr_story[j]*(time_scale[i]-time_story[j-1]) + revr_story[j-1]*(time_story[j]-time_scale[i])) / (time_story[j]-time_story[j-1]))
            rescaled_diff_story.append((diff_story[j]*(time_scale[i]-time_story[j-1]) + diff_story[j-1]*(time_story[j]-time_scale[i])) / (time_story[j]-time_story[j-1]))
    
    return rescaled_revr_story, rescaled_diff_story