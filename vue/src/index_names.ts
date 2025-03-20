export const assay_types=["salmonella","campylobactor","ecoli"]
export const sub_types=["assay","SRA","Nucleotide","BioSample","BioProject"]
export const index_names={
    "salmonella":{
        "assay":"salmonella-assay-index-v4",
        "SRA":"salmonella-sra-index-v5",
        "Nucleotide":"salmonella-nucleotide-index-v5",
        "BioSample":"bio-sample-index",
        "BioProject":"salmonella-bioproject-index-v4"
    },
    "campylobactor":{
        "assay":"campylobactor-assay-index",
        "SRA":"campylobactor_sra_new",
        "Nucleotide":"campylobactor_nucleotide_new",
        "BioSample":"campylobactor_biosample_new",
        "BioProject":"campylobactor_bioproject_new"
    },
    "ecoli":{  
        "assay":"ecoli_assay_index",
        "SRA":"ecoli_sra_index",
        "Nucleotide":"ecoli_nucleotide_index",
        "BioProject":"ecoli_bioproject_index"   
    }
}